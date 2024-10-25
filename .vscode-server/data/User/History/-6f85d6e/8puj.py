#----------------crawl--------------------
import re
import json
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
#------------------------airflow-----------------------
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
#-------------------kafka----------------------------
from confluent_kafka import Producer

# def selenium_scraper():
def selenium_scraper():
    def error_cb(err):
        print('Error: %s' % err)
    # 步驟1. 設定要連線到Kafka集群的相關設定
    props = {
        # Kafka集群在那裡?
        'bootstrap.servers': '104.155.214.8:9092',  # <-- 置換成要連接的Kafka集群
        'max.in.flight.requests.per.connection': 1,
        'error_cb': error_cb                    # 設定接收error訊息的callback函數
    }
    # 步驟2. 產生一個Kafka的Producer的實例
    producer = Producer(props)
    # 步驟3. 指定想要發佈訊息的topic名稱
    topicName = 'dcard-topic'

    # 設定 ChromeOptions
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 無頭模式，沒有 GUI
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    #參數
    dcard_url = "https://www.dcard.tw/f/tech_job"
    # 一次爬幾個文章
    num_articles = 1
    # 中間會有阻擋的，要跳過(每個版不同)
    block = 7
    # 每個版的頭不同，data-key不同
    head = 1
    # 使用 webdriver_manager 安裝 ChromeDriver，並讓 WebDriver 自動找到
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_window_size(1920, 1080)
    driver.get("https://www.google.com")
    search = driver.find_element(By.NAME, "q")
    search.send_keys(f"{dcard_url}")
    search.send_keys(Keys.ENTER)
    sleep(10)  # 最多等待 10 秒
    driver.find_element(By.XPATH, f"//*[@id='rso']/div[1]/div/div/div/div/div/div/div/div[1]/div/span/a[@href='{dcard_url}']").click()
    # 等待頁面載入
    sleep(10)  # 最多等待 10 秒
    for i in range(head, num_articles+head):
    # 預防爬的過程出問題，還是可以把爬到的存下來
        # try:
            # 中間會有別板的，要跳過
            if i == block:
                continue
            # 抓取連結
            element_by_data_key = driver.find_element(By.XPATH, f"//div[@data-key='{i}']")
            url = element_by_data_key.find_element(By.CLASS_NAME, "t1gihpsa").get_attribute("href")
            # 抓取文章ID
            article_ID = url.split('/')[-1]
            # 使用第二個瀏覽器(用來爬文章內容)
            driver1 = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            driver1.set_window_size(1920, 1080)
            driver1.get('https://www.google.com')
            # 定位google搜尋的位置
            search = driver1.find_element(By.NAME, "q")
            search.send_keys(f"{url}")
            search.send_keys(Keys.ENTER)
            sleep(10)
            # 如果搜尋不到文章，就會跳過
            try:
                # 進入dcard文章
                driver1.find_element(By.XPATH, f"//*[@id='rso']/div[1]/div/div/div/div[1]/div/div/span/a[@href='{url}']").click()
                sleep(10)
            except Exception:
                driver1.quit()
                driver.execute_script("arguments[0].scrollIntoView({block:'start'});", element_by_data_key)
                continue
            # 抓取標題
            title = driver1.find_element(By.CLASS_NAME, "t17vlqzd").text
            # 抓取看版類型
            type = driver1.find_element(By.CLASS_NAME, f"tcjsomj").text   
            # 抓取作者
            author = driver1.find_element(By.CLASS_NAME, f"avvspio").text
            # 抓取發布時間(抓的時間是格林威治標準時間，所以還要再+8才是台灣時間)
            # time = driver1.find_element(By.TAG_NAME, "time").get_attribute('datetime')
            # 抓取emoji數
            try:
                emoji_num = driver1.find_element(By.CLASS_NAME, f"s1r6dl9").text
            except Exception:
                emoji_num = 0
            # 抓取hash tag
            try:
                hash_tag = []
                element_by_hash_tag = driver1.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div[2]/div/div/div/div/article/div[3]/div').text
                for word in element_by_hash_tag.split('\n'):
                    hash_tag.append(word)
            except Exception:
                hash_tag = []
            # 抓取文章內容
            article_content = ''
            element_by_class = driver1.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div[2]/div/div/div/div/article/div[2]/div/div')
            element_by_span = element_by_class.find_elements(By.TAG_NAME, "span")
            # 將文章內容存成字串
            for span in element_by_span:
                content = re.findall(r'.{1}',span.text)
                for word in content:
                    article_content += word
            # 進入emoji小頁面
            try:
                # 先移到開啟emoji小頁面的地方
                test = driver1.find_element(By.CLASS_NAME, 'r1skb6m4')
                driver1.execute_script("arguments[0].scrollIntoView({block:'center'});", test)
                driver1.find_element(By.CLASS_NAME, 'r1skb6m4').click()
                sleep(2)
                # 各個emoji數
                emojis = []
                type_emoji = {}
                element_by_emojis = driver1.find_elements(By.CLASS_NAME, 'irn7u4a')
                for each in element_by_emojis:
                    key = each.text.split('\n')[0]
                    value  = each.text.split('\n')[1]
                    type_emoji[key] = value
                emojis.append(type_emoji)
            except Exception:
                emojis = []
            # 離開小頁面
            exit = driver1.find_element(By.CLASS_NAME, 'mn4uf0t')
            exit.send_keys(Keys.ESCAPE)
            # 移至留言區
            mes_start = driver1.find_element(By.CLASS_NAME, 'd1vdw76m')
            driver1.execute_script("arguments[0].scrollIntoView({block:'center'});", mes_start)
            # 如果找得到新至舊的留言區就使用，沒有就直接爬
            try:
                driver1.find_elements(By.CLASS_NAME, 'oqcw3sj')[1].click()
            except NoSuchElementException:
                pass
            except IndexError:
                pass
            sleep(10)
            # 爬取留言
            messages = []
            each_message = {}
            message_no = {}
            # 定位第一個留言
            i = int(driver1.find_element(By.CLASS_NAME, 'c1cbe1w2').get_attribute('data-doorplate'))

            move = 0
            while True:
                while True:
                    try:    
                        # 定位留言區域
                        count = 1
                        data_doorplate = driver1.find_element(By.CSS_SELECTOR, f'div[data-doorplate="{i}"]')
                        driver1.execute_script("arguments[0].scrollIntoView({block:'start'});", data_doorplate)
                        break
                    except Exception:
                        # 如果找不到下一個留言，就往下滑直到找到，當滑動十次還找不到，就代表已經滑到最底了，可以結束
                        driver1.execute_script("window.scrollBy(0, 500);")
                        move += count
                        if move == 10:
                            break
                        sleep(0.5)
                if move == 10:
                    break
                try:
                    message = data_doorplate.find_element(By.CLASS_NAME, f'c19xyhzv')
                    mes_no = message.find_element(By.CLASS_NAME, f'dl7cym2').text
                    mes_writer = message.find_element(By.CLASS_NAME, f'tygfsru').text
                    mes_content = message.find_element(By.CLASS_NAME, f'c1ehvwc9').text
                    mes_time = message.find_element(By.TAG_NAME, 'time').get_attribute('datetime')
                    message_no[mes_no] = {'用戶': mes_writer, '內容': mes_content, '時間': mes_time}
                    messages.append(message_no)
                    message_no = {}
                except Exception:
                    i += 1
                    continue
                i += 1
                driver1.execute_script("arguments[0].scrollIntoView({block:'start'});", message)
                sleep(1)
            # 離開文章
            sleep(10)
            driver1.quit()

            data1 = {
                "文章ID": article_ID, 
                "作者": author, 
                "標題": title, 
                "連結": url, 
                "發布時間": time, 
                "內容": article_content, 
                "總emoji數": emoji_num, 
                "emoji類型": emojis, 
                "留言":messages, 
                "hash_tag": hash_tag, 
                "看版": type}
            json_data = json.dumps(data1, ensure_ascii=False)
            producer.produce(topicName, key = url, value = json_data.encode('utf-8'))
            producer.flush()
            print(f"已傳送文章至 Kafka: {title}")
            print(data1)
            # 頁面向下滾動
            driver.execute_script("arguments[0].scrollIntoView({block:'start'});", element_by_data_key)
            sleep(0.5)
        # except Exception:
        #     driver1.quit()
        #     continue 
    driver.quit()
    print(data1)
# 設置默認參數
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 10, 24),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 定義 DAG
with DAG(
    'test3',
    default_args=default_args,
    description='A simple Selenium DAG',
    schedule_interval=timedelta(days=1),  # 每天運行一次
    catchup=False,
) as dag:

    run_selenium_task = PythonOperator(
        task_id='run_selenium_task',
        python_callable=selenium_scraper
    )