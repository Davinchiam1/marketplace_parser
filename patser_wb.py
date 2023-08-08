import datetime
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd


def scrap_feedbaks(sku_list=[],max_numb=4000, end_date=None, filename='feedbacks'):
    """
       Getting data about product reviews by parsing reviews from product page on Wildberries.

        Args:
            sku_list (list): list of sku (unic id on marketplace)
            max_numb (int): max number of reviews per sku
            end_date (string): date by which reviews must be uploaded
            filename (string): name for result file

        Returns:
            None
    """

    writer = pd.ExcelWriter(filename + '.xlsx')
    end_date = datetime.datetime.strptime(end_date, "%d %B %Y")
    temp_frame = pd.DataFrame()
    for sku in sku_list:

        url = 'https://www.wildberries.ru/catalog/'+str(sku)+'/feedbacks'

        # Launch the Chrome browser and open the reviews page

        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        # Waiting for the page to fully load
        wait = WebDriverWait(driver, 20)
        wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "ul.comments__list[data-link]")))
        total_reviews = driver.find_elements(By.XPATH, '//span[@class="product-feedbacks__count"]')
        total_reviews = int(total_reviews[0].text)
        if total_reviews>= max_numb:
            total_reviews=max_numb
        print(total_reviews)

        df = pd.DataFrame(columns=['Rating', 'Text', 'Date'])
        flag=True
        # Scroll to the bottom of the page
        while True:
            # Scroll the page to the end
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.randint(1, 10))  # We pause for 1-10 seconds to download content and bypass blocking

            # Check if all reviews are loaded
            reviews = driver.find_elements(By.XPATH, './/li[@class="comments__item feedback j-feedback-slide"]')
            if len(reviews) >= total_reviews:  # If enough reviews have been loaded, exit the loop
                break
            last_review = reviews[-1]
            last_date=last_review.find_element(By.XPATH, './/span[@class="feedback__date hide-desktop"]').get_attribute('content')
            last_date=datetime.datetime.strptime(last_date.split('T')[0], "%Y-%m-%d")
            if last_date<end_date:
                break
        time.sleep(2)
        feedbaks = driver.find_elements(By.CLASS_NAME, 'comments__item.feedback.j-feedback-slide')
        for feedbak in feedbaks:
            feedback_text = feedbak.find_element(By.XPATH, './/p[@class="feedback__text"]').text
            rating_element = feedbak.find_element(By.CSS_SELECTOR, "span.feedback__rating").get_attribute("class")
            rating = int(rating_element.split("star")[-1])
            date = feedbak.find_element(By.XPATH, '//span[@class="feedback__date hide-desktop"]').get_attribute('content')
            date = date.split('T')[0] + ' ' + date.split('T')[1][:-1]
            df = pd.concat(
                [df, pd.DataFrame({'Rating': [rating], 'Text': [feedback_text], 'Date': [date]})],
                ignore_index=True)
        if len(sku_list) > 9:
            temp_frame = pd.concat([temp_frame, df], axis=0)
        else:
            df.to_excel(writer, sheet_name=str(sku))
            print('---' * 10)

        # Close the browser
        driver.quit()
    if len(sku_list) > 9:
        temp_frame.to_excel(writer, sheet_name='main')
    writer.close()
    print('Finished')

# scrap_feedbaks(['97833688'], end_date='1 June 2023', filename='test4')