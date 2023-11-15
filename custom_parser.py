import datetime
import random
import traceback

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
# import re
import regex as re
import time
import pandas as pd


class Custom_parser():
    """Class for small parsers for unic purposes"""

    def __init__(self, url_file=None, url_colum="URL", filename='feedbaks'):
        self.url_file = url_file
        self.url_colum = url_colum
        self.filename = filename

    def scrap_profiles(self):
        """Load profile info from AZ inluensers accounts"""
        temp_frame = pd.read_excel(self.url_file)
        url_list = list(temp_frame[self.url_colum])
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=chrome_options)
        df = pd.DataFrame(columns=['Name', 'Url', 'Description'])
        for elem, url in enumerate(url_list):

            url = url.split('/ref')[0]
            # Pause after first page
            if elem > 0:
                time.sleep(random.randint(2, 10))
                print(elem)
            else:
                driver.get(url)
                driver.delete_all_cookies()

            # Launch the Chrome browser and open the reviews page

            driver.get(url)

            wait = WebDriverWait(driver, 40)
            # driver.refresh()

            # Waiting for the page to fully load
            time.sleep(random.randint(1, 4))
            wait = WebDriverWait(driver, 40)
            sotials = {}
            try:
                info = driver.find_element(By.CSS_SELECTOR, "#shop-influencer-grid-section.a-row")

                name = info.find_element(By.ID, "shop-influencer-profile-name").text
                description = info.find_element(By.ID, "shop-influencer-profile-description-text").text
                try:
                    links = info.find_elements(By.CSS_SELECTOR, 'a.a-link-normal')
                    links = links[1:]
                    for link in links:
                        social = link.get_attribute("href")
                        socials_group = social.split('.')
                        if 'www' in social:
                            socials_group = socials_group[1]
                        else:
                            socials_group = socials_group[0].split('://')[1]
                        if socials_group not in df.columns:
                            df[socials_group] = ''
                        sotials[socials_group] = social
                except Exception as e:
                    print(e)
                    traceback.print_exc()
                    pass
            except:
                info = driver.find_element(By.CSS_SELECTOR, 'div.a-section.name-header-bio-container')
                name = info.find_element(By.ID, 'oap-name').text
                description = 'Amazon Verified user'

            record = {'Name': name, 'Url': url, 'Description': description}
            record.update(sotials)
            df.loc[len(df)] = record
        df.to_excel(self.filename + ".xlsx")
        driver.quit()
        print('Finished')

    def scrap_data(self):
        """Get data from specific fields in product data page from WB"""
        temp_frame = pd.read_excel(self.url_file)
        url_list = list(temp_frame[self.url_colum].drop_duplicates())
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=chrome_options)
        df = pd.DataFrame(columns=['id', 'Материал посуды'])
        # df['id']=temp_frame['id']
        start_time = time.time()
        for elem, url in enumerate(url_list):
            # Pause after first page
            try:
                if elem > 0:
                    time.sleep(random.randint(2, 10))
                    print(elem)
                else:
                    driver.delete_all_cookies()

                # Launch the Chrome browser and open the reviews page
                driver.get(url)

                wait = WebDriverWait(driver, 40)
                # driver.refresh()

                # Waiting for the page to fully load
                time.sleep(random.randint(1, 4))
                wait = WebDriverWait(driver, 40)
                try:
                    element = driver.find_element(By.XPATH, '//tr[.//span[contains(text(), "Материал посуды")]]')

                    # Get the value from the corresponding td element
                    # value = element.find_element(By.XPATH, './/td/span').text
                    value = driver.execute_script("return arguments[0].innerText;", element)
                    numbers = re.findall(r'\d+', value)
                    # Print the value
                    print("Value:", value)
                except NoSuchElementException:
                    numbers = 'Нет данных'
                record = {'id': url.split('/')[4], 'Материал посуды': numbers}
                df.loc[len(df)] = record
            except Exception as e:
                df.to_excel(self.filename + ".xlsx")
                end_time = time.time()
                execution_time = end_time - start_time
                print(f"Время выполнения программы: {execution_time} секунд")

        driver.quit()
        df.to_excel(self.filename + ".xlsx")
        driver.quit()
        print('Finished')

    def get_photos(url_file=None, url_colum="URL"):
        """Load photo links to AZ products"""
        temp_frame = pd.read_excel(url_file)
        url_list = list(temp_frame[url_colum])
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=chrome_options)
        photo_links = []
        for elem, url in enumerate(url_list):

            # Pause after first page
            if elem > 0:
                time.sleep(random.randint(2, 10))
                print(elem)
                driver.get(url)
            else:
                driver.get(url)
                driver.delete_all_cookies()

            wait = WebDriverWait(driver, 40)
            driver.refresh()

            # Waiting for the page to fully load
            time.sleep(random.randint(1, 4))
            wait = WebDriverWait(driver, 40)
            try:
                photo_link = driver.find_element(By.CSS_SELECTOR, "#landingImage").get_attribute('src')
                photo_links.append(photo_link)
            except:
                photo_links.append('')
        temp_frame['Photo links'] = photo_links
        temp_frame.to_excel(url_file)
        driver.quit()
        print('Finished')


Custom_parser(url_file='D:\\Аналитика\\WB_Ozon\\для отчетов\\графины\\urls.xlsx', url_colum='url').scrap_data()

#
#
# scrap(
#     url_file='Z:\\Аналитика\\WB_Ozon\\Mpstat\\Исследование категорий\\мужской крем для лица\\очищено\Уход за лицом и телом Крем 01.06.2022-01.06.2023.xlsx',
#     filename='vols1')
# url = 'https://www.amazon.com/Garden-Life-Organics-Vitamins-Certified/product-reviews/B06XSDP7RX'
