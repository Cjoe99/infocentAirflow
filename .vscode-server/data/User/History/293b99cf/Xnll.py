from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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
        http_conn_id='slack_webhook',
        message=slack_msg,
        channel='#4-自動化排程',  # 指定你的 Slack 頻道
        dag=context['dag']
    )
    return failure_notification.execute(context=context)

# Selenium 抓取任務
def selenium_scraper():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 無頭模式，沒有 GUI
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        driver.get("https://www.google.com")
        print("Page title is:", driver.title)

        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys("Selenium")
        search_box.submit()

        driver.implicitly_wait(10)  # 最多等待 10 秒
        print("New page title is:", driver.title)
    finally:
        driver.quit()

# 設置默認參數
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 10, 22),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'on_failure_callback': slack_failure_callback,  # 失敗時的回調
}

# 定義 DAG
with DAG(
    'selenium_scraper_dag_with_slack',
    default_args=default_args,
    description='Selenium scraping DAG with Slack notifications',
    schedule_interval=timedelta(days=1),  # 每天運行一次
    catchup=False,
) as dag:

    # 執行 Selenium 抓取任務
    run_selenium_task = PythonOperator(
        task_id='run_selenium_task',
        python_callable=selenium_scraper,
        retries=3  # 如果失敗會重試3次
    )

    # 成功時發送 Slack 通知
    slack_success_notification = SlackWebhookOperator(
        task_id='slack_success_notification',
        slack_webhook_conn_id='slack_webhook',
        message=":white_check_mark: Selenium scraping task completed successfully in Airflow.",
        channel='#your-channel'  # 指定你的 Slack 頻道
    )

    # 任務流程：執行抓取任務 -> 成功後發送 Slack 通知
    run_selenium_task >> slack_success_notification
