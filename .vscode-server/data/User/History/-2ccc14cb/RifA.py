from selenium import webdriver
from selenium.webdriver.common.by import By

# 設定 ChromeOptions
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 無頭模式，沒有 GUI
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# 啟動 Chrome 瀏覽器
driver = webdriver.Chrome(options=options)

try:
    # 打開 Google 網頁
    driver.get("https://www.google.com")

    # 確認頁面標題
    print("Page title is:", driver.title)

    # 找到搜尋框，輸入 "Selenium" 並提交
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys("Selenium")
    search_box.submit()

    # 等待頁面加載並確認新標題
    driver.implicitly_wait(10)  # 最多等待 10 秒
    print("New page title is:", driver.title)

finally:
    # 關閉瀏覽器
    driver.quit()
