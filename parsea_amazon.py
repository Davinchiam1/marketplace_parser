import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd

url = 'https://www.amazon.com/Garden-Life-Organics-Vitamins-Certified/product-reviews/B06XSDP7RX'

# Запускаем браузер Chrome и открываем страницу с отзывами

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
options = chrome_options
driver = webdriver.Chrome()
driver.get(url)

df = pd.DataFrame(columns=['Rating', 'Text', 'Date and Region'])

while True:
    # Ждем, пока страница полностью загрузится
    time.sleep(random.randint(1, 4))
    wait = WebDriverWait(driver, 40)
    reviews = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.a-section.review.aok-relative")))
    page_reviews = driver.find_elements(By.CSS_SELECTOR, "div.a-section.review.aok-relative")

    for review in page_reviews:
        rating = review.find_element(By.CSS_SELECTOR, 'a.a-link-normal').accessible_name
        date = review.find_element(By.CSS_SELECTOR, '.a-size-base.a-color-secondary.review-date').text
        title = review.find_element(By.CSS_SELECTOR,
                                    '.a-size-base.a-link-normal.review-title.a-color-base.review-title-content.a-text'
                                    '-bold').text
        text = review.find_element(By.CSS_SELECTOR, "div.a-row.a-spacing-small.review-data").text
        df = pd.concat(
            [df, pd.DataFrame({'Rating': [rating], 'Text': [title + '/' + text], 'Date and Region': [date]})],
            ignore_index=True)

    time.sleep(random.randint(1, 10))
    driver.refresh()
    wait = WebDriverWait(driver, 40)
    next_button = driver.find_element(By.CSS_SELECTOR, "li.a-last")
    if next_button.get_attribute("class") != 'a-disabled a-last':
        next_button.click()
        print(1)
    else:
        break

driver.quit()
print(df)
