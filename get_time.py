from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
def get_time(company,code,name, max_retries=3):
    retries = 0
    while retries < max_retries:
        # 設定選項
        options = Options()
        options.add_argument('--headless')  # 啟用無頭模式
        options.add_argument('--disable-gpu')  # 如果你使用的是 Windows，需要禁用 GPU
        options.add_argument('--disable-dev-shm-usage')  # 防止共享內存問題
        # 初始化 WebDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        try:
            if(company=='元大'):
                driver.get(f'https://www.yuantaetfs.com/tradeInfo/pcf/{code}')
                driver.implicitly_wait(10)
                target_row = driver.find_element(By.XPATH, "//div[@class='tr' and .//div[text()='平均票息率(%)']]")
                percent = target_row.find_element(By.XPATH, ".//div[@class='td info'][1]//span[not(@class)]").text
                target_row = driver.find_element(By.XPATH, "//div[@class='tr' and .//div[contains(text(), '存續期間')]]")
                year = target_row.find_element(By.XPATH, ".//div[@class='td info'][1]//span[not(@class)]").text
                # 印出第一個數值
                driver.quit()
                return percent,year
                #print(target_row.get_attribute('outerHTML'))
            elif(company=='國泰'):
                driver.get(f'https://www.cathaysite.com.tw/ETF/product?keyword={code}')
                wait = WebDriverWait(driver, 10)  # 最長等待 10 秒
                target_div = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, f"//div[contains(@class, 'cursor-pointer') and contains(., '{code}') and contains(., '{company}')]")
                    )
                )
                target_div.click()
                #print("當前頁面 URL:", driver.current_url)
                time.sleep(2)
                wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "loading")))
                holdings_tab = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//a[contains(text(), '持股權重')]")
                    )
                )
                holdings_tab.click()
                rate_row = wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//tr[th[contains(text(), '平均票息率(%)')]]")
                    )
                )
                percent = rate_row.find_element(By.XPATH, "./td[1]").text  # 獲取第一個 <td> 的值
                rate_row = wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//tr[th[contains(text(), '存續期間')]]")
                    )
                )
                year=rate_row.find_element(By.XPATH, "./td[1]").text
                #print(first_value,year)
                driver.quit()
                return percent,year
            elif(company=='富邦'):
                if(code=='00718B'):
                    driver.get('https://websys.fsit.com.tw/FubonETF/Trade/Assets.aspx?stkId=00718B&ddate=20241128&lan=TW')
                else:
                    driver.get(f'https://websys.fsit.com.tw/FubonETF/Fund/Assets.aspx?stkId={code}')
                wait = WebDriverWait(driver, 10)
                close_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@class='agree']/button"))
                )
                close_button.click()
                time.sleep(2)
                table = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//table[contains(@class, 'table1') and contains(@class, 'etf2')]"))
                )
                # 抓取「平均票息率」的第一個值
                avg_coupon_rate_row = table.find_element(By.XPATH, ".//tr[td[contains(text(), '平均票息率')]]")
                percent = avg_coupon_rate_row.find_element(By.XPATH, "./td[2]").text
        
                # 抓取包含「存續期間」的行的第一個值
                avg_duration_row = table.find_element(By.XPATH, ".//tr[td[contains(text(), '存續期間')]]")
                year = avg_duration_row.find_element(By.XPATH, "./td[2]").text
                # 打印結果
                #print("平均票息率的第一個值:", percent)
                #print("存續期間的第一個值:", year)
                driver.quit()
                return percent,year
            elif(company=='群益'):
                driver.get('https://www.capitalfund.com.tw/etf/product/overview')
                wait = WebDriverWait(driver, 10)  # 最長等待 10 秒
                target_a = wait.until(
                    EC.presence_of_element_located((By.XPATH, f"//div[@class='td-mobile']/a[text()='{code}']"))
                )
                href_value = target_a.get_attribute("href")
                #print(f"代碼 {code} 的 href 值:", href_value)
                driver.get(href_value+'/buyback')
                time.sleep(2)
                # 等待並點擊「持債特性」按鈕
                characteristics_tab = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@class='tab-item']/a[contains(text(), '持債特性')]"))
                )
                characteristics_tab.click()
                # 等待「平均票息率」欄位出現
                avg_coupon_row = wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@class='tr' and .//div[@class='td-mobile' and text()='平均票息率(%)']]")
                    )
                )
        
                # 抓取第一個數值
                percent = avg_coupon_row.find_element(By.XPATH, "./div[@class='td']/div[@class='td-mobile']").text
                # 抓取「存續期間」的第一個值
                duration_row = wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@class='tr' and .//div[contains(text(), '存續期間')]]")
                    )
                )
                year = duration_row.find_element(By.XPATH, "./div[@class='td']/div[@class='td-mobile']").text
                driver.quit()
                return percent,year
            elif(company=='復華'):
                driver.get('https://www.fhtrust.com.tw/ETF/etf_list')
                wait = WebDriverWait(driver, 10)  # 最長等待 10 秒
                # 找到包含代碼的目標行
                target_row = wait.until(
                    EC.presence_of_element_located((By.XPATH, f"//tbody/tr[@class='fundListTable-fundCard etfListTable-fundCard' and .//td[contains(text(), '{code}')]]"))
                )
                # 抓取 <a> 的 href
                fund_link = target_row.find_element(
                    By.XPATH, ".//a"
                ).get_attribute("href")
                #print(f"原始 href: {fund_link}")
        
                # 替換 #nav 為 #stockhold
                updated_link = fund_link.replace("#nav", "#stockhold")
                #print(f"更新後的 href: {updated_link}")
        
                # 重新訪問更新後的 URL
                driver.get(updated_link)
                #print(f"已導航到更新後的 URL: {updated_link}")
                wait = WebDriverWait(driver, 30)
                time.sleep(2)
                # 抓取「平均票息率」的第一個值
                avg_coupon_rate_row = wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//tr[.//td[contains(text(), '平均票息率')]]")
                    )
                )
                percent = avg_coupon_rate_row.find_element(
                    By.XPATH, "./td[@class='text-right'][1]//span"
                ).text
                #print("平均票息率的第一個數值:", avg_coupon_rate)
        
                # 抓取「平均修正存續期間」的第一個值
                duration_row = wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//tr[.//td[contains(text(), '存續期間')]]")
                    )
                )
                year = duration_row.find_element(
                    By.XPATH, "./td[@class='text-right'][1]//span"
                ).text
                #print("平均修正存續期間的第一個數值:", duration)
                driver.quit()
                return percent,year
            elif(company=="凱基"):
                driver.get('https://www.kgifund.com.tw/Fund/RedemptionList#')
                wait = WebDriverWait(driver, 10)  # 最長等待 10 秒
                agree_button = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//a[@onclick=\"ClickETFWarningOption('同意')\"]")
                    )
                )
                #print("找到按鈕:", agree_button.get_attribute("outerHTML"))
                # 使用 JavaScript 替換 onclick 行為
                driver.execute_script("arguments[0].click();", agree_button)
                #print("成功點擊『同意』按鈕")
                # 等待頁面加載完成
                wait.until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                time.sleep(2)
                # 定位「債券ETF」的卡片標題
                bond_etf_button = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//a[.//span[text()='債券ETF']]")
                    )
                )
                #print(bond_etf_button.get_attribute('outerHTML'))
                # 點擊「債券ETF」卡片
                bond_etf_button.click()
                # 定位 <select> 元素
                select_element = wait.until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "js-redemption-select")
                    )
                )
                if(name=="凱基ESG BBB 債 15+"):name="凱基ESG BBB債15+"
                # 使用 Select 類選擇對應的基金名稱
                select = Select(select_element)
                select.select_by_visible_text(name)
                #print(f"成功選擇基金: {name}")
                # 抓取「平均票息利率(%)」的第一個數值
                percent = wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//li[.//span[contains(text(), '平均票息利率')]]/span[2]")
                    )
                ).text
                #print("平均票息利率(%):", avg_coupon_rate)
        
                # 抓取「存續期間(年)」的第一個數值
                year = wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//li[.//span[contains(text(), '存續期間')]]/span[2]")
                    )
                ).text
                #print("存續期間(年):", duration)
                driver.quit()
                return percent,year
            elif(company=="中信"):
                driver.get('https://www.ctbcinvestments.com.tw/Product/ETFArea')
                wait = WebDriverWait(driver, 10)  # 最長等待 10 秒
                # 定位並點擊「債券型ETF」
                bond_etf_tab = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//a[@href='#type4' and text()='債券型ETF']")
                    )
                )
                driver.execute_script("arguments[0].click();", bond_etf_tab)
                #print("成功點擊『債券型ETF』")
                time.sleep(2)
                # 等待「債券型ETF」對應的表格加載
                wait.until(
                    EC.presence_of_element_located(
                        (By.ID, "type4")
                    )
                )
        
                # 根據基金名稱定位對應的鏈接
                fund_link = wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, f"//td[@data-title='基金名稱']/a[contains(text(), '{name}')]")
                    )
                )
                #fund_href = fund_link.get_attribute("href")
                #print(f"找到基金名稱『{name}』對應的鏈接: {fund_href}")
        
                # 點擊進入該基金的詳細頁面
                driver.execute_script("arguments[0].click();", fund_link)
                #print(f"成功進入基金『{name}』的詳細頁面")
        
                # 點擊「投資組合」標籤
                portfolio_tab = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//a[@name='Link5' and text()='投資組合']")
                    )
                )
                driver.execute_script("arguments[0].click();", portfolio_tab)
                #print("成功點擊『投資組合』標籤")
        
                # 等待目標表格加載完成
                table = wait.until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "etf-table")
                    )
                )
                #print(table.get_attribute('outerHTML'))
                # 增加穩定性：強制等待表格內容渲染
                time.sleep(2)
                # 抓取「平均票息率」的第一個數值
                percent = table.find_element(
                    By.XPATH, ".//tr[td[contains(text(), '平均票息率')]]/td[2]"
                ).text
                #print("平均票息率(%):", percent)
        
                # 抓取「存續期間」的第一個數值
                year = table.find_element(
                    By.XPATH, ".//tr[td[contains(text(), '存續期間')]]/td[2]"
                ).text
                #print("存續期間(年):",year)
                driver.quit()
                return percent,year
            elif(company=='永豐'):
                driver.get(f'https://sitc.sinopac.com/SinopacEtfs/Etfs/Pcf/{code}')
                wait = WebDriverWait(driver, 10)  # 最長等待 10 秒
                # 限定範圍至包含「持債特性」的 cash_box
                cash_boxes = wait.until(
                    EC.presence_of_all_elements_located(
                        (By.CLASS_NAME, "cash_box")
                    )
                )
                #print(f"找到 {len(cash_boxes)} 個 cash_box 容器")
                
                # 鎖定包含「持債特性」的容器
                target_cash_box = None
                for cash_box in cash_boxes:
                    try:
                        title = cash_box.find_element(By.CLASS_NAME, "cash_title-s").text
                        if "持債特性" in title:
                            target_cash_box = cash_box
                            #print("成功定位到包含『持債特性』的容器")
                            break
                    except Exception:
                        continue
        
                if not target_cash_box:
                    #print("未找到包含『持債特性』的容器")
                    return
                # 抓取「平均票息率」的第一個值
                avg_coupon_rate_element = cash_box.find_element(
                    By.XPATH, ".//table[@class='tab_sh tab_sh-w tab_fu-06']//tr[td[contains(text(), '平均票息率')]]/td[2]"
                )
                percent = avg_coupon_rate_element.text.strip()
                #print("平均票息率(%):", percent)
        
                # 抓取「平均有效存續期間」的第一個值
                duration_element = cash_box.find_element(
                    By.XPATH, ".//table[@class='tab_sh tab_sh-w tab_fu-06']//tr[td[contains(text(), '存續期間')]]/td[2]"
                )
                year = duration_element.text.strip()
                #print("平均有效存續期間(年):", year)
                driver.quit()
                return percent,year
            elif(company=='統一'):
                driver.get("https://www.ezmoney.com.tw/ETF/Fund")
                wait = WebDriverWait(driver, 10)  # 最長等待 10 秒
                # 確保表格加載完成
                table = wait.until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "table-bordered")
                    )
                )
                #print("成功加載表格")
        
                # 找到對應代碼的 href
                fund_row = table.find_element(
                    By.XPATH,
                    f".//tr[td/dl/dd/span[text()='{code}']]//a"
                )
                #fund_href = fund_row.get_attribute("href")
                #print(f"找到基金代碼 {code} 的鏈接: {fund_href}")
        
                # 點擊進入該基金的詳細頁面
                driver.execute_script("arguments[0].click();", fund_row)
                #print(f"成功進入基金『{name}』的詳細頁面")
                time.sleep(2)
                # 等待表格加載完成
                tables = wait.until(
                    EC.presence_of_all_elements_located(
                        (By.CLASS_NAME, "table-bordered")
                    )
                )
        
                # 遍歷找到包含「平均票息率」的表格
                target_table = None
                for table in tables:
                    try:
                        if table.find_element(By.XPATH, ".//tr/td[contains(text(), '平均票息率')]"):
                            target_table = table
                            break
                    except:
                        continue
        
                #print("成功定位包含『平均票息率』的表格")
                time.sleep(2)
                # 抓取「平均票息率」的第一個值
                avg_coupon_rate_row = target_table.find_element(
                    By.XPATH, ".//tr[td[contains(text(), '平均票息率')]]"
                )
                #print(avg_coupon_rate_row.get_attribute('outerHTML'))
                avg_coupon_rate_cell = target_table.find_element(By.XPATH, ".//tr[td[contains(text(), '平均票息率')]]/td[2]")
                percent = avg_coupon_rate_cell.get_attribute("textContent").strip()
                #print("目標單元格完整 HTML:", avg_coupon_rate_cell.get_attribute("outerHTML"))
                #print("平均票息率(%):", percent)
        
                # 抓取「存續期間」的第一個值
                duration = target_table.find_element(
                    By.XPATH, ".//tr[td[contains(text(), '存續期間')]]/td[2]"
                )
                year=duration.get_attribute("textContent").strip()
                #print("存續期間(年):", year)
                driver.quit()
                return percent,year
            elif(company=="台新"):
                if(code=="00842B"):
                    driver.get("https://www.tsit.com.tw/ETF?Tag=PurchaseTag&KindId=2119&FundId=16050")
                elif(code=="00942B"):
                    driver.get("https://www.tsit.com.tw/ETF?Tag=PurchaseTag&KindId=2119&FundId=16086")
                elif(code=="00734B"):
                    driver.get("https://www.tsit.com.tw/ETF?Tag=PurchaseTag&KindId=2119&FundId=15970")
                else: return "",""
                wait = WebDriverWait(driver, 10)  # 最長等待 10 秒
                # 獲取所有表格
                all_tables = driver.find_elements(By.XPATH, "//table[@class='m-table m-mix-table m-add-color']")
                #print(f"找到 {len(all_tables)} 個表格")
            
                target_table = None
            
                # 遍歷表格，找到包含目標字段的表格
                for table in all_tables:
                    if "平均票息率" in table.get_attribute('outerHTML'):
                        target_table = table
                        break
            
                #if not target_table:
                    #print("未找到包含『平均票息率』的表格")
                #else:
                    #print("成功定位包含『平均票息率』的表格")
                    #print(target_table.get_attribute('outerHTML'))
            
                    # 抓取「平均票息率」的第一個值
                avg_coupon_rate_cell = target_table.find_element(
                    By.XPATH, ".//tr[td/em[contains(normalize-space(), '平均票息率')]]/td[2]"
                )
                percent = avg_coupon_rate_cell.text.strip()
                #print("平均票息率(%):", avg_coupon_rate)
        
                # 抓取「存續期間」的第一個值
                duration_cell = target_table.find_element(
                    By.XPATH, ".//tr[td/em[contains(normalize-space(), '存續期間')]]/td[2]"
                )
                year = duration_cell.text.strip()
                #print("存續期間(年):", duration)
                driver.quit()
                return percent,year
            elif(company=="新光"):
                driver.get(f"http://etf.skit.com.tw/Home/ETFSeriesDetail/{code}")
                wait = WebDriverWait(driver, 10)  # 最長等待 10 秒
                portfolio_tab = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@href='#paneFive1' and text()='投資組合']"))
                )
                driver.execute_script("arguments[0].click();", portfolio_tab)
                #print("成功点击『投资组合』选项卡")
                # 查找所有 panel-danger 的 div
                time.sleep(3)
                panels = driver.find_elements(By.CLASS_NAME, "panel-danger")
                target_table = None
                
                # 遍历 panels，找到包含『持债特性』的表格
                for panel in panels:
                    #print(panel.get_attribute('outerHTML'))
                    try:
                        heading = panel.find_element(By.CLASS_NAME, "panel-heading").text
                        #print(heading)
                        if "持債特性" in heading:
                            target_table = panel.find_element(By.CLASS_NAME, "table-striped")
                            #print("成功找到『持债特性』表格")
                            break
                    except Exception as e:
                        continue
                if not target_table:
                    raise Exception("未找到包含『持债特性』的表格")
                percent = target_table.find_element(
                    By.XPATH, ".//tr[td[contains(text(), '平均票息率')]]/td[2]"
                ).text.strip()
                #print("平均票息率(%):", avg_coupon_rate)
            
                year = target_table.find_element(
                    By.XPATH, ".//tr[td[contains(text(), '存續期間')]]/td[2]"
                ).text.strip()
                #print("存续期间(年):", duration)
                driver.quit()
                return percent,year
            elif(company=="第一"):
                return "",""
        except (TimeoutException, StaleElementReferenceException, NoSuchElementException, WebDriverException) as e:
            print(f"出現錯誤: {e}. 第 {retries + 1} 次重試...")
            retries += 1
            driver.quit()
            if retries >= max_retries:
                print("達到最大重試次數，退出...")
                driver.quit()
                return "", ""
#print(get_time("富邦", "00718B", "富邦中國政策債"))