from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
import requests
from bs4 import BeautifulSoup
import time
import json
from confluent_kafka import Producer
from datetime import datetime, timedelta
import gc

def frank_ptt():
    max_pages = 2000  # 設定要爬取的最大頁數
    current_page = 1  # 目前爬取的頁面，初始為1

    # 用來接收從Consumer instance發出的error訊息
    def error_cb(err):
        print('Error: %s' % err)

    # Kafka 設定
    kafka_config = {
        # Kafka集群在那裡?
        'bootstrap.servers': '104.155.214.8:9092',  # <-- 置換成要連接的Kafka集群
        'max.in.flight.requests.per.connection': 1, 
        'error_cb': error_cb  # 設定接收error訊息的callback函數
    }

    producer = Producer(kafka_config)
    topic = 'test-topic'  # 替換為你的 Kafka topic 名稱

    base_url = "https://www.ptt.cc"
    board_url = "/bbs/Gossiping/index39062.html"
    cookies = {'over18': '1'}

    def delivery_report(err, msg):
        """回報訊息傳送狀態"""
        if err is not None:
            print(f"訊息傳送失敗: {err}")
        else:
            print(f"訊息成功傳送到 {msg.topic()} 分區 [{msg.partition()}]")

    def get_post_content(link):
        try:
            response = requests.get(link, cookies=cookies)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            content = soup.find('div', id='main-content')
            meta_info = soup.find_all('span', class_='article-meta-value')
            author = meta_info[0].text.strip() if len(meta_info) > 0 else "未知"

            pushes = soup.find_all('div', class_='push')
            push_count, boo_count, arrow_count = 0, 0, 0
            comments = []

            for push in pushes:
                push_tag_element = push.find('span', class_='push-tag')
                if push_tag_element:
                    push_tag = push_tag_element.text.strip()
                else:
                    break  
                push_user = push.find('span', class_='push-userid').text.strip()
                push_content = push.find('span', class_='push-content').text.strip()
                push_time = push.find('span', class_='push-ipdatetime').text.strip()

                if push_tag == '推':
                    push_count += 1
                elif push_tag == '噓':
                    boo_count += 1
                else:
                    arrow_count += 1

                comments.append({
                    "推文": push_tag,
                    "用戶": push_user,
                    "內容": push_content[2:],
                    "時間": push_time
                })

            if content:
                for tag in content.find_all(['span', 'div']):
                    tag.extract()
                return {
                    "作者": author,
                    "內容": content.text.strip(),
                    "推": push_count,
                    "噓": boo_count,
                    "箭頭": arrow_count,
                    "留言": comments
                }
        except requests.RequestException as e:
            print(f"抓取文章內容時發生錯誤: {e}")
        return {}

    # 日期格式轉換函數
    def convert_date(date_str):
        try:
            return datetime.strptime(date_str, '%m/%d')
        except ValueError as e:
            print(f"日期轉換失敗: {e}")
            return {}

    while current_page < max_pages :
        try:
            response = requests.get(base_url + board_url, cookies=cookies)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            posts = soup.find_all('div', class_='r-ent')

            for post in posts:
                a_tag = post.find('a')
                if a_tag:
                    title = a_tag.text.strip()
                    link = base_url + a_tag['href']
                    post_data = get_post_content(link)
                    date_str = post.find('div', class_='date').text.strip()
                    post_date = convert_date(date_str)

                    if post_data:
                        post_document = {
                            "發佈日期": date_str,
                            "標題": title,
                            "作者": post_data["作者"],
                            "內容": post_data["內容"],
                            "推": post_data["推"],
                            "噓": post_data["噓"],
                            "箭頭": post_data["箭頭"],
                            "連結": link,
                            "留言": post_data["留言"]
                        }

                        # 將文章資料轉換為 JSON 格式
                        json_data = json.dumps(post_document, ensure_ascii=False)

                        # 將資料傳送到 Kafka
                        producer.produce(topic, key=link, value=json_data.encode('utf-8'), callback=delivery_report)
                        producer.flush()  # 確保訊息已傳送

                        print(f"已傳送文章至 Kafka: {title}")

            btn_group = soup.find('div', class_='btn-group btn-group-paging')
            prev_link = btn_group.find_all('a')[1]['href']
            board_url = prev_link
            print(f"第{current_page}頁完成")
            del soup, posts, response, btn_group, prev_link
            gc.collect()  # 強制執行垃圾回收
            current_page += 1  # 頁數遞增   
            time.sleep(1)
        except requests.RequestException as e:
            print(f"抓取頁面時發生錯誤: {e}")
            break

# 定義在失敗時發送 Slack 通知的回調函數
def slack_failure_callback(context):
    slack_msg = f"""
        :red_circle: Task Failed.
        *Task*: {context.get('task_instance').task_id}  
        *Dag*: {context.get('task_instance').dag_id}  
        *Execution Time*: {context.get('execution_date')}  
        *Log URL*: {context.get('task_instance').log_url}
    """
    failure_notification = SlackWebhookOperator(
        task_id='slack_failure_notification',
        slack_webhook_conn_id='slack_webhook',  # 連接到你在 Airflow Connections 中配置的 Slack Webhook
        message=slack_msg,
        dag=context['dag']
    )
    return failure_notification.execute(context=context)

# 設置默認參數
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 10, 22),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'on_failure_callback': slack_failure_callback,  # 失敗時發送 Slack 通知
}

# 定義 DAG
with DAG(
    'frank_dag',
    default_args=default_args,
    description='A simple ptt DAG',
    schedule_interval=timedelta(days=1),
    catchup=False,
) as dag:

    run_selenium_task = PythonOperator(
        task_id='run_selenium_task',
        python_callable=frank_ptt
    )

    slack_success_notification = SlackWebhookOperator(
        task_id='slack_success_notification',
        slack_webhook_conn_id='slack_webhook',  # 連接到你在 Airflow Connections 中配置的 Slack Webhook
        message="frank_dag completed successfully in Airflow."
    )
