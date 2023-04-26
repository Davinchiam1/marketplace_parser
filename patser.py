import selenium
import requests
import pandas
from bs4 import BeautifulSoup
#
# # URL страницы с отзывами о товаре
# url = 'https://www.wildberries.ru/catalog/149469867/feedbacks'
#
# # Заголовки для запроса
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
#
# # Отправляем запрос на получение страницы
# response = requests.get(url, headers=headers)
#
# # Создаем объект Beautiful Soup
# soup = BeautifulSoup(response.content, 'html.parser')
#
# # Находим все отзывы на странице
# reviews = soup.find_all(' ul', {'class': 'comments__list'})
#
# # Выводим текст каждого отзыва
# for review in reviews:
#     print(review.find('div', {'class': 'feedback__text'}).text)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

url = 'https://www.wildberries.ru/catalog/51450143/feedbacks'

# Запускаем браузер Chrome и открываем страницу с отзывами
driver = webdriver.Chrome()
driver.get(url)

# Ждем, пока страница полностью загрузится
wait = WebDriverWait(driver, 20)
reviews = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.comments__list[data-link]")))
total_reviews = driver.find_elements(By.XPATH, '//span[@class="product-feedbacks__count"]')
total_reviews = int(total_reviews[0].text)
print(total_reviews)

# Прокручиваем страницу до конца
while True:
    # Скроллим страницу до конца
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Делаем паузу на 2 секунды для загрузки контента

    # Проверяем, загружены ли все отзывы
    reviews = driver.find_elements(By.XPATH, './/p[@class="feedback__text"]')
    if len(reviews) >= total_reviews:  # Если загружено достаточное количество отзывов, выходим из цикла
        break
feedback_texts = driver.find_elements(By.XPATH, './/p[@class="feedback__text"]')
for feedback_text in feedback_texts:
    print(feedback_text.text)
print(len(feedback_texts))
# for review in reviews:
#     review_text = review.find_element_by_css_selector('.feedback__text').text
#     print(review_text)

# Закрываем браузер
driver.quit()
