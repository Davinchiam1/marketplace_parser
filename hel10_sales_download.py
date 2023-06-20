import glob
import os
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

human_inter = None


def _rename_files_in_folder(folder_path, keyword='chart', asin_list=None):
    csv_files = glob.glob(os.path.join(folder_path, f"*{keyword}*.csv"))
    csv_files.sort(key=os.path.getctime)

    if len(csv_files) != len(asin_list):
        print("Количество файлов и новых имен должно быть одинаковым.")
        return

    for file, new_name in zip(csv_files, asin_list):
        new_file_path = os.path.join(folder_path, new_name)
        os.rename(file, new_file_path+'.csv')
        print(f"Файл {file} переименован в {new_name}.")


def load_sales(asin_list=None, login_text='denissdolzhenkov@gmail.com', password_text='#R0v5*I0BU!s'):
    # Путь к файлу расширения .crx
    extension_path = 'helium.crx'
    extension_path = os.path.abspath(extension_path)
    global human_inter

    # Создание объекта ChromeOptions и указание пути к расширению
    chrome_options = Options()
    chrome_options.add_extension(extension_path)

    # Инициализация драйвера Chrome
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://members.helium10.com/user/signup?type=chrome-extension')
    handles = driver.window_handles
    driver.switch_to.window(handles[1])
    driver.close()
    driver.switch_to.window(handles[0])

    wait = WebDriverWait(driver, 10)
    element = driver.find_element(By.CSS_SELECTOR, "a.signup-form-bottom__link")
    element.click()

    login = driver.find_element(By.CSS_SELECTOR, "input#loginform-email")
    login.send_keys(login_text)
    wait = WebDriverWait(driver, 10)

    password = driver.find_element(By.CSS_SELECTOR, "input#loginform-password")
    password.send_keys(password_text)
    wait = WebDriverWait(driver, 10)

    element = driver.find_element(By.CSS_SELECTOR, "button.btn.btn-secondary.btn-block")
    element.click()
    time.sleep(random.randint(5, 10))
    human_inter = True

    for asin in asin_list:

        driver.get('https://www.amazon.com/dp/' + asin)

        while human_inter:
            time.sleep(1)
        wait = WebDriverWait(driver, 20)  # Максимальное время ожидания в секундах
        open_graph = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc-ga-dRe")))
        # open_graph = driver.find_element(By.CSS_SELECTOR, "div.sc-ga-dRe")
        time.sleep(random.randint(1, 3))
        try:
            open_graph.click()
        except Exception as exp:
            driver.refresh()
            wait = WebDriverWait(driver, 20)  # Максимальное время ожидания в секундах
            open_graph = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc-ga-dRe")))
            time.sleep(random.randint(1, 3))
            open_graph.click()
        time.sleep(random.randint(1, 3))

        all_time = driver.find_element(By.XPATH, "//li[contains(text(), 'All Time')]")
        all_time.click()
        time.sleep(random.randint(1, 3))

        menu = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="View chart menu"]')))
        menu.click()
        time.sleep(random.randint(1, 3))

        download = driver.find_element(By.XPATH, "//li[text()='Download CSV']")
        download.click()
        time.sleep(random.randint(5, 10))
        _rename_files_in_folder(folder_path=os.path.join(os.path.expanduser("~"), "Downloads"), asin_list=[asin])

    # _rename_files_in_folder(folder_path=os.path.join(os.path.expanduser("~"), "Downloads"),asin_list=asin_list)


# Находим элемент, содержащий shadow DOM
# element = driver.find_element(By.CSS_SELECTOR, '#h10-page-widget > div')
#
# # Выполняем скрипт для получения элемента внутри shadow DOM
# sub_element = element.shadow_root
# element=sub_element.find_element(By.CSS_SELECTOR,'div.sc-ePwGgO.cHqWHe.react-draggable')
# element.click()
# # sub_element = element.shadow_root
# # load= sub_element.find_elements(By.CSS_SELECTOR,'button.sc-kBPahn.loPNhA.sc-dKjDRw.gDtPYH')
# # load[-1].click()
# # load= driver.find_element(By.CSS_SELECTOR,'button[data-testid="close-button"]')
# # load.click()
# time.sleep(5)
# driver.refresh()
# print('refreshed')
# load_sales(asin_list='asins.xlsx')

