# #-------------airflow--------------------------
# from airflow import DAG
# from datetime import date, datetime, timedelta
# from airflow.operators.python import PythonOperator
# #--------------爬蟲----------------------------
# import re
# import json
# from time import sleep
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.common.exceptions import NoSuchElementException

# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# #---------------kafka-------------------------
# from confluent_kafka import Producer

# def crawl_dcard():
#     # 用來接收從Consumer instance發出的error訊息
#     def error_cb(err):
#         print('Error: %s' % err)
#     # 步驟1. 設定要連線到Kafka集群的相關設定
#     props = {
#         # Kafka集群在那裡?
#         'bootstrap.servers': '104.155.214.8:9092',  # <-- 置換成要連接的Kafka集群
#         'max.in.flight.requests.per.connection': 1,
#         'error_cb': error_cb                    # 設定接收error訊息的callback函數
#     }
#     # 步驟2. 產生一個Kafka的Producer的實例
#     producer = Producer(props)
#     # 步驟3. 指定想要發佈訊息的topic名稱
#     topicName = 'dcard-topic'
# #--------------------------------爬蟲-----------------------------------------
#     # 使用 undetected_chromedriver 初始化 Chrome 瀏覽器 (用來爬標題和連結)
#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless')  # 無頭模式，沒有 GUI
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("user-agent=Your User Agent String")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--remote-debugging-port=9222")
#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
#     driver.set_window_size(1920, 1080)
#     # driver = uc.Chrome()
#     # 前往dcard 科技業版
#     dcard_url = "https://www.dcard.tw/f/tech_job" 
#     driver.get(dcard_url)
#     # 等待頁面載入
#     sleep(10)
#     # 一次爬幾個文章
#     num_articles = 30
#     # 中間會有阻擋的，要跳過(每個版不同)
#     block = 7
#     # 每個版的頭不同，data-key不同
#     head = 1
#     for i in range(head, num_articles+head):
#         # 預防爬的過程出問題，還是可以把爬到的存下來
#         try:
#             # 中間會有別板的，要跳過
#             if i == block:
#                 continue
#             # 抓取連結
#             element_by_data_key = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, f"//div[@data-key='{i}']")))
#             # element_by_data_key = driver.find_element(By.XPATH, f"//div[@data-key='{i}']")
#             url = element_by_data_key.find_element(By.TAG_NAME, "a").get_attribute("href")
#             # 抓取文章ID
#             article_ID = url.split('/')[-1]
#             # 使用第二個瀏覽器(用來爬文章內容)
#             # driver1 = uc.Chrome()
#             driver1 = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
#             driver1.set_window_size(1920, 1080)
#             driver1.get('https://www.google.com')
#             # 定位google搜尋的位置
#             search = driver1.find_element(By.NAME, "q")
#             search.send_keys(f"{url}")
#             search.send_keys(Keys.ENTER)
#             sleep(10)
#             # 如果搜尋不到文章，就會跳過
#             try:
#                 # 進入dcard文章
#                 driver1.find_element(By.XPATH, f"//*[@id='rso']/div[1]/div/div/div/div[1]/div/div/span/a[@href='{url}']").click()
#                 sleep(10)
#             except Exception:
#                 driver1.quit()
#                 driver.execute_script("arguments[0].scrollIntoView({block:'start'});", element_by_data_key)
#                 continue
#             # 抓取標題
#             title = driver1.find_element(By.CLASS_NAME, "t17vlqzd").text
#             # 抓取看版類型
#             type = driver1.find_element(By.CLASS_NAME, f"tcjsomj").text   
#             # 抓取作者
#             author = driver1.find_element(By.CLASS_NAME, f"avvspio").text
#             # 抓取發布時間(抓的時間是格林威治標準時間，所以還要再+8才是台灣時間)
#             time = driver1.find_element(By.TAG_NAME, "time").get_attribute('datetime')
#             # 抓取emoji數
#             try:
#                 emoji_num = driver1.find_element(By.CLASS_NAME, f"s1r6dl9").text
#             except Exception:
#                 emoji_num = 0
#             # 抓取hash tag
#             try:
#                 hash_tag = []
#                 element_by_hash_tag = driver1.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div[2]/div/div/div/div/article/div[3]/div').text
#                 for word in element_by_hash_tag.split('\n'):
#                     hash_tag.append(word)
#             except Exception:
#                 hash_tag = []
#             # 抓取文章內容
#             article_content = ''
#             element_by_class = driver1.find_element(By.XPATH, '//*[@id="__next"]/div[2]/div[2]/div/div/div/div/article/div[2]/div/div')
#             element_by_span = element_by_class.find_elements(By.TAG_NAME, "span")
#             # 將文章內容存成字串
#             for span in element_by_span:
#                 content = re.findall(r'.{1}',span.text)
#                 for word in content:
#                     article_content += word
#             # 進入emoji小頁面
#             try:
#                 # 先移到開啟emoji小頁面的地方
#                 test = driver1.find_element(By.CLASS_NAME, 'r1skb6m4')
#                 driver1.execute_script("arguments[0].scrollIntoView({block:'center'});", test)
#                 driver1.find_element(By.CLASS_NAME, 'r1skb6m4').click()
#                 sleep(2)
#                 # 各個emoji數
#                 emojis = []
#                 type_emoji = {}
#                 element_by_emojis = driver1.find_elements(By.CLASS_NAME, 'irn7u4a')
#                 for each in element_by_emojis:
#                     key = each.text.split('\n')[0]
#                     value  = each.text.split('\n')[1]
#                     type_emoji[key] = value
#                 emojis.append(type_emoji)
#             except Exception:
#                 emojis = []
#             # 離開小頁面
#             driver1.find_element(By.CLASS_NAME, 'mfgatba').click()
#             # 移至留言區
#             mes_start = driver1.find_element(By.CLASS_NAME, 'd1vdw76m')
#             driver1.execute_script("arguments[0].scrollIntoView({block:'center'});", mes_start)
#             # 如果找得到新至舊的留言區就使用，沒有就直接爬
#             try:
#                 driver1.find_elements(By.CLASS_NAME, 'oqcw3sj')[2].click()
#             except NoSuchElementException:
#                 pass
#             except IndexError:
#                 pass
#             sleep(10)
#             # 爬取留言
#             messages = []
#             each_message = {}
#             message_no = {}
#             # 定位第一個留言
#             i = int(driver1.find_element(By.CLASS_NAME, 'c1cbe1w2').get_attribute('data-doorplate'))
#             # 如果是新至舊的留言，從最新跑到最舊
#             if i > 1:
#                 while i >= 1:
#                     # 定位留言區域
#                     data_doorplate = driver1.find_element(By.CSS_SELECTOR, f'div[data-doorplate="{i}"]')
#                     message = data_doorplate.find_element(By.CLASS_NAME, f'c19xyhzv')
#                     try:
#                         # 抓取樓數
#                         mes_no = message.find_element(By.CLASS_NAME, f'dl7cym2').text
#                         # 抓取留言者
#                         mes_writer = message.find_element(By.CLASS_NAME, f'tygfsru').text
#                         # 抓取內容
#                         mes_content = message.find_element(By.CLASS_NAME, f'c1ehvwc9').text
#                         # 抓取時間(他用的是GMT)
#                         mes_time = message.find_element(By.TAG_NAME, 'time').get_attribute('datetime')
#                         message_no[mes_no] = {'用戶': mes_writer, '內容': mes_content, '時間': mes_time}
#                         messages.append(message_no)
#                         message_no = {}
#                     except Exception:
#                         i -= 1
#                         continue
#                     i -= 1
#                     driver1.execute_script("arguments[0].scrollIntoView({block:'start'});", message)
#                     sleep(1)
#             # 如果是一般的留言
#             else:
#                 while True:
#                     try:
#                         data_doorplate = driver1.find_element(By.CSS_SELECTOR, f'div[data-doorplate="{i}"]')
#                         message = data_doorplate.find_element(By.CLASS_NAME, f'c19xyhzv')
#                     except NoSuchElementException:
#                         break
#                     try:
#                         mes_no = message.find_element(By.CLASS_NAME, f'dl7cym2').text
#                         mes_writer = message.find_element(By.CLASS_NAME, f'tygfsru').text
#                         mes_content = message.find_element(By.CLASS_NAME, f'c1ehvwc9').text
#                         mes_time = message.find_element(By.TAG_NAME, 'time').get_attribute('datetime')
#                         message_no[mes_no] = {'用戶': mes_writer, '內容': mes_content, '時間': mes_time}
#                         messages.append(message_no)
#                         message_no = {}
#                     except Exception:
#                         i += 1
#                         continue
#                     i += 1
#                     driver1.execute_script("arguments[0].scrollIntoView({block:'start'});", message)
#                     sleep(1)
#             # 離開文章
#             sleep(10)
#             driver1.quit()

#             data1 = {
#                 "文章ID": article_ID, 
#                 "作者": author, 
#                 "標題": title, 
#                 "連結": url, 
#                 "發布時間": time, 
#                 "內容": article_content, 
#                 "總emoji數": emoji_num, 
#                 "emoji類型": emojis, 
#                 "留言":messages, 
#                 "hash_tag": hash_tag, 
#                 "看版": type}
#             json_data = json.dumps(data1, ensure_ascii=False)
#             producer.produce(topicName, key = url, value = json_data.encode('utf-8'))
#             producer.flush()
#             print(f"已傳送文章至 Kafka: {title}")
#             # 頁面向下滾動
#             driver.execute_script("arguments[0].scrollIntoView({block:'start'});", element_by_data_key)
#             sleep(10)
#         except Exception:
#             driver1.quit()
#             continue 
#     driver.quit()
# # 設置默認參數
# default_args = {
#     'owner': 'airflow',
#     'depends_on_past': False,
#     'start_date': datetime(2024, 10, 23),
#     'retries': 1,
#     'retry_delay': timedelta(minutes=5),
# }
# # 定義 DAG
# with DAG(
#     'dcard_dag',
#     default_args=default_args,
#     description='A simple dcard DAG',
#     schedule_interval=timedelta(days=1),  # 每天運行一次
#     catchup=False,
# ) as dag:

#     run_selenium_task = PythonOperator(
#     task_id='run_crawl_task',
#         python_callable = crawl_dcard
#     )

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys

def selenium_scraper():
    # 設定 ChromeOptions
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 無頭模式，沒有 GUI
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # 使用 webdriver_manager 安裝 ChromeDriver，並讓 WebDriver 自動找到
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    url = 'https://www.dcard.tw/f/tech_job'
    try:
        driver.get("https://www.google.com")
        search = driver.find_element(By.NAME, "q")
        search.send_keys(f"{url}")
        search.send_keys(Keys.ENTER)
        driver.implicitly_wait(10)  # 最多等待 10 秒
        driver.find_element(By.TAG_NAME, f'a[@href="{url}"]').click()
        driver.implicitly_wait(10)  # 最多等待 10 秒
        print("Page title is:", driver.title)

        # search_box = driver.find_element(By.NAME, "q")
        # search_box.send_keys("Selenium")
        # search_box.submit()

        
        # print("New page title is:", driver.title)

    finally:
        driver.quit()

# 設置默認參數
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 10, 23),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# 定義 DAG
with DAG(
    'test',
    default_args=default_args,
    description='A simple Selenium DAG',
    schedule_interval=timedelta(days=1),  # 每天運行一次
    catchup=False,
) as dag:

    run_selenium_task = PythonOperator(
        task_id='run_selenium_task',
        python_callable=selenium_scraper
    )