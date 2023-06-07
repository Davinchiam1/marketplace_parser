import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
# import re
import regex as re
import time
import pandas as pd


def scrap_feedbaks(sku_list=[], max_numb=2000, end_mounth=None, filename='feedbaks'):
    writer = pd.ExcelWriter(filename + '.xlsx')
    for elem, sku in enumerate(sku_list):

        if elem > 0:
            time.sleep(random.randint(20, 40))
        url = 'https://www.amazon.com/t/product-reviews/' + str(sku)
        index = 0
        flag = False

        # Запускаем браузер Chrome и открываем страницу с отзывами

        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        df = pd.DataFrame(columns=['Rating', 'Status', 'Text', 'Date', 'Region'])
        pattern = r"(?<=\w)(?=[A-Z])"
        wait = WebDriverWait(driver, 40)
        driver.refresh()
        sort = driver.find_element(By.CSS_SELECTOR, 'span.a-button-text.a-declarative[data-action="a-dropdown-button"]')
        sort.click()
        option = driver.find_element(By.ID, "sort-order-dropdown_1")
        option.click()
        # driver.execute_script("arguments[0].click();", sort_dropdown)
        # time.sleep(5)
        # sort.click()

        while index < max_numb:
            # Ждем, пока страница полностью загрузится
            time.sleep(random.randint(1, 4))
            wait = WebDriverWait(driver, 40)
            reviews = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.a-section.review.aok-relative")))
            page_reviews = driver.find_elements(By.CSS_SELECTOR, "div.a-section.review.aok-relative")

            for review in page_reviews:
                try:
                    rating = review.find_element(By.CSS_SELECTOR, 'a.a-link-normal').accessible_name
                    status = review.find_element(By.CSS_SELECTOR, 'span[data-hook="avp-badge"]').text
                    date_reg = review.find_element(By.CSS_SELECTOR, '.a-size-base.a-color-secondary.review-date').text
                    region, date = date_reg.split('on')
                    title = review.find_element(By.CSS_SELECTOR,
                                                '.a-size-base.a-link-normal.review-title.a-color-base.review-title'
                                                '-content.a-text-bold').text
                    text = review.find_element(By.CSS_SELECTOR, "div.a-row.a-spacing-small.review-data").text
                    record = {'Rating': rating, 'Status': status, 'Text': title + '/' + text, 'Date': date,
                              'Region': region}
                    try:
                        add_info = review.find_element(By.CSS_SELECTOR, 'a[data-hook="format-strip"]')
                        asin=add_info.get_attribute("href").split(sep='/')[5]
                        link=add_info.get_attribute("href")
                        add_info=add_info.text

                    except Exception as ex:
                        pass
                    if add_info:
                        split_strings = re.split(pattern, add_info)
                        split_strings.append('Asin: '+asin)
                        split_strings.append('Link: ' + link)
                        for category in split_strings:
                            category=category.split(sep=': ', maxsplit=1)
                            if category[0] not in df.columns:
                                df[category[0]]=''
                            record[category[0]]=category[1]

                    # df = pd.concat([df, pd.DataFrame(record)], ignore_index=True)
                    df.loc[len(df)] = record
                    if end_mounth in date:
                        flag = True
                        break
                except Exception as e:
                    df['Date'] = pd.to_datetime(df['Date'])
                    df.to_excel(writer, sheet_name=str(sku))
            index = index + 10
            if flag:
                break
            time.sleep(random.randint(1, 10))
            driver.refresh()
            wait = WebDriverWait(driver, 40)
            next_button = driver.find_element(By.CSS_SELECTOR, "li.a-last")
            if next_button.get_attribute("class") != 'a-disabled a-last':
                next_button.click()
                print(index)
            else:
                break

        driver.quit()
        df['Date'] = pd.to_datetime(df['Date'])
        df.to_excel(writer, sheet_name=str(sku))
        print('---' * 10)
    writer.close()


scrap_feedbaks(['B07DM8XQ9C'], end_mounth='May', filename='allergy & immune')
# url = 'https://www.amazon.com/Garden-Life-Organics-Vitamins-Certified/product-reviews/B06XSDP7RX'
