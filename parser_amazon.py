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


def scrap_feedbaks(sku_list=[], max_numb=4000, end_date=None, filename='feedbaks', by_stars=True):
    """
       Getting data about product reviews by parsing reviews from product page on Amazon.

        Args:
            sku_list (list): list of sku (unic id on marketplace)
            max_numb (int): max number of reviews per sku
            end_date (string): date by which reviews must be uploaded
            filename (string): name for result file
            by_stars (bool): load by star rating, default True

        Returns:
            None
    """
    writer = pd.ExcelWriter(filename + '.xlsx')
    end_date=datetime.datetime.strptime(end_date, "%d %B %Y")
    temp_frame=pd.DataFrame()
    if by_stars:
        total = pd.DataFrame(columns=['Stars', 'Ratings', 'Reviews', 'Asin'])
    for elem, sku in enumerate(sku_list):

        # Pause after first page
        if elem > 0:
            time.sleep(random.randint(20, 40))
        url = 'https://www.amazon.com/t/product-reviews/' + str(sku)
        index = 0
        flag = False
        if by_stars:
            num=0
            rate_list=[str(5),str(4),str(3),str(2),str(1)]

        # Launch the Chrome browser and open the reviews page

        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        driver.delete_all_cookies()

        # Create base dataframe
        df = pd.DataFrame(columns=['Rating', 'Status', 'Text', 'Date', 'Region','Link','Influencer','Main_Asin'])
        pattern = r"(?<=\w|\))(?=[A-Z])"
        wait = WebDriverWait(driver, 30)
        driver.refresh()

        # Sort by most resent
        try:
            sort = driver.find_element(By.CSS_SELECTOR, 'span.a-button-text.a-declarative[data-action="a-dropdown-button"]')
            sort.click()
            option = driver.find_element(By.ID, "sort-order-dropdown_1")
            option.click()
        except NoSuchElementException:
            driver.close()
            time.sleep(random.randint(20, 40))
            driver.delete_all_cookies()
            driver.get(url)
            driver.refresh()
            sort = driver.find_element(By.CSS_SELECTOR,
                                       'span.a-button-text.a-declarative[data-action="a-dropdown-button"]')
            sort.click()
            option = driver.find_element(By.ID, "sort-order-dropdown_1")
            option.click()
        # driver.execute_script("arguments[0].click();", sort_dropdown)
        # time.sleep(5)
        # sort.click()

        while index < max_numb:
            # Waiting for the page to fully load
            if by_stars and (index ==0 or index==100):
                flag=False
                time.sleep(1)
                ratings = driver.find_element(By.CSS_SELECTOR, '#a-autoid-5-announce')
                ratings.click()
                time.sleep(1)
                box=driver.find_element(By.XPATH, f"//a[@class='a-dropdown-link' and text()='{rate_list[num]} star only']")
                box.click()
                marks_count = driver.find_element(By.CSS_SELECTOR,'div.a-row.a-spacing-base.a-size-base').text.split('total ratings,')
                total.loc[len(total)] = {'Stars': rate_list[num], 'Ratings': marks_count[0].replace(",", ""),
                                         'Reviews': marks_count[1].split('with')[0].replace(",", ""),'Asin':sku}


            time.sleep(random.randint(1, 4))
            wait = WebDriverWait(driver, 30)
            reviews = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.a-section.review.aok-relative")))
            # Load all review in page(10 units)
            page_reviews = driver.find_elements(By.CSS_SELECTOR, "div.a-section.review.aok-relative")


            for review in page_reviews:
                exp = None
                try:
                    # Load main fields in review
                    rating = review.find_element(By.CSS_SELECTOR, 'i[data-hook="review-star-rating"] span.a-icon-alt').get_attribute("innerHTML")

                    try:
                        status = review.find_element(By.CSS_SELECTOR, 'span[data-hook="avp-badge"]').text
                    except NoSuchElementException:
                        try:
                            status = review.find_element(By.XPATH, '//span[contains(@class, "a-color-success") and contains(@class, "a-text-bold")]').text
                        except:
                            status='Unverified'
                    date_reg = review.find_element(By.CSS_SELECTOR, '.a-size-base.a-color-secondary.review-date').text
                    region, date = date_reg.split('on')
                    title = review.find_element(By.CSS_SELECTOR,
                                                '.a-size-base.a-link-normal.review-title.a-color-base.review-title'
                                                '-content.a-text-bold')
                    link=title.get_attribute("href")
                    title=title.text
                    text = review.find_element(By.CSS_SELECTOR, "div.a-row.a-spacing-small.review-data").text
                    record = {'Rating': rating, 'Status': status, 'Text': title + '/' + text, 'Date': date,
                              'Region': region,'Link':link, 'Main_Asin':sku}

                    # finding if review is created by influencer
                    customer=review.find_element(By.CSS_SELECTOR,"a.a-profile")
                    if customer.get_attribute("data-a-verified"):
                        record['Influencer'] = customer.get_attribute("href")
                    else:
                        record['Influencer']='No'

                    # Finding additional info fields
                    try:
                        add_info = review.find_element(By.CSS_SELECTOR, 'a[data-hook="format-strip"]')
                        asin=add_info.get_attribute("href").split(sep='/')[5]
                        add_info=add_info.text

                    except NoSuchElementException:
                        add_info=False
                        pass
                    if add_info:
                        split_strings = re.split(pattern, add_info)
                        result = [split_strings[0]]
                        j=0

                        for i in range(1, len(split_strings)):
                            if len(split_strings[i]) < 3 or ':' not in split_strings[i]:
                                result[j] += split_strings[i]
                            else:
                                result.append(split_strings[i])
                                j+=1
                        split_strings=result

                        split_strings.append('Asin: '+asin)
                        for category in split_strings:
                            category=category.split(sep=': ', maxsplit=1)
                            if category[0] not in df.columns:
                                df[category[0]]=''
                            record[category[0]]=category[1]

                    # df = pd.concat([df, pd.DataFrame(record)], ignore_index=True)
                    df.loc[len(df)] = record
                    if datetime.datetime.strptime(date.strip(), "%B %d, %Y") < end_date:
                        flag = True
                        print('brake2')
                        break
                except Exception as exp:
                    print(exp)
                    time.sleep(10)
                    traceback.print_exc()
                    df['Date'] = pd.to_datetime(df['Date'])
                    if len(sku_list) > 9:
                        temp_frame=pd.concat([temp_frame, df], axis=0)
                        temp_frame.to_excel('intervediate'+filename + '.xlsx')
                    else:
                        df.to_excel(writer, sheet_name=str(sku))
            index = index + 10
            if by_stars and (index==100 or flag):
                print(index)
                num=num+1
                index = 0
                if num == 5:
                    break
                continue
            if flag:
                break
            time.sleep(random.randint(1, 7))
            # driver.refresh()
            wait = WebDriverWait(driver, 30)
            # Load new page
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "li.a-last")
            except NoSuchElementException:
                if by_stars:
                    if int(marks_count[1].split('with')[0].replace(",", ""))<100:
                        break
            if next_button.get_attribute("class") != 'a-disabled a-last':
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.randint(1, 4))
                next_button.click()
                print(index)
            else:
                if by_stars:
                    num = num + 1
                    index=0
                    if num ==5:
                        break
                    continue
                print('brake1')
                break

        driver.quit()
        df['Date'] = pd.to_datetime(df['Date'])
        # if list of products is too big, concat in one list, elsr
        if len(sku_list) > 9:
            temp_frame=pd.concat([temp_frame, df], axis=0)
        else:
            df.to_excel(writer, sheet_name=str(sku))
        print('---' * 10)
    if by_stars:
        total.to_excel(writer,sheet_name='total')
    if len(sku_list) > 9:
        temp_frame.to_excel(writer, sheet_name='main')
    print('Finished')
    writer.close()


# scrap_feedbaks(['B00280M13O','B079YXFCWT'], end_date='1 January 2021', filename='test5')
# url = 'https://www.amazon.com/Garden-Life-Organics-Vitamins-Certified/product-reviews/B06XSDP7RX'
