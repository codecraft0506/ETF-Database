from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

url = "https://www.macromicro.me/etf/tw/intro/00679B"

options = Options()
# 模擬人類的 User-Agent
options.set_preference("general.useragent.override", 
                       "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

driver = webdriver.Firefox(options=options)
driver.get(url)

try:
    btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="nav-dividend"]'))
    )

    actions = ActionChains(driver)
    actions.move_to_element(btn).click().perform()

    data = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="content--dividend"]/div/div[2]/p'))
    ).text.strip()

    print(data)

except Exception as e:
    print("Error:", e)

finally:
    driver.quit()
