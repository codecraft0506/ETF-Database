from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://www.macromicro.me/etf/tw/intro/00679B"

options = Options()
options.set_preference("general.useragent.override", 
                       "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

driver = webdriver.Firefox(options=options)
driver.get(url)

# Wait for the page to load
WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.ID, 'nav-dividend'))
).click()

# Wait for the dividend content to load
data_element = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '#content--dividend div.your-target-class'))
)

data = data_element.text.strip()
print(data)

driver.quit()
