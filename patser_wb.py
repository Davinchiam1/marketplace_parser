import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd


def scrap_feedbaks(sku_list=[]):

    for sku in sku_list:

        url = 'https://www.wildberries.ru/catalog/'+str(sku)+'/feedbacks'

        # Запускаем браузер Chrome и открываем страницу с отзывами

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        # Ждем, пока страница полностью загрузится
        wait = WebDriverWait(driver, 20)
        wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "ul.comments__list[data-link]")))
        total_reviews = driver.find_elements(By.XPATH, '//span[@class="product-feedbacks__count"]')
        total_reviews = int(total_reviews[0].text)
        print(total_reviews)

        df = pd.DataFrame(columns=['Rating', 'Text', 'Date'])

        # Прокручиваем страницу до конца
        while True:
            # Скроллим страницу до конца
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.randint(1, 10))  # Делаем паузу на 1-10 секунд для загрузки контента и обхода блокировки

            # Проверяем, загружены ли все отзывы
            reviews = driver.find_elements(By.XPATH, './/p[@class="feedback__text"]')
            if len(reviews) >= total_reviews:  # Если загружено достаточное количество отзывов, выходим из цикла
                break
        time.sleep(2)
        feedbaks = driver.find_elements(By.CLASS_NAME, 'comments__item.feedback.j-feedback-slide')
        for feedbak in feedbaks:
            feedback_text = feedbak.find_element(By.XPATH, './/p[@class="feedback__text"]').text
            rating_element = feedbak.find_element(By.CSS_SELECTOR, "span.feedback__rating").get_attribute("class")
            rating = int(rating_element.split("star")[-1])
            date = feedbak.find_element(By.CSS_SELECTOR, 'span.feedback__date').get_attribute('content')
            date = date.split('T')[0] + ' ' + date.split('T')[1][:-1]
            df = pd.concat(
                [df, pd.DataFrame({'Rating': [rating], 'Text': [feedback_text], 'Date': [date]})],
                ignore_index=True)
        name = 'reviews ' + str(sku)
        df.to_excel(name)

        # Закрываем браузер
        driver.quit()
    print('Finished')
