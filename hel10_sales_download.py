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
    """
       Renaming files in destination folder, which contain keyword in file name .

        Args:
            folder_path (string): path to folder with target files
            keyword (string): keyword to detect target files in folder
            asin_list (list): list of new file names

        Returns:
            None
    """
    # detect files
    csv_files = glob.glob(os.path.join(folder_path, f"*{keyword}*.csv"))
    csv_files.sort(key=os.path.getctime)

    # check amount of files
    if len(csv_files) != len(asin_list):
        print("Количество файлов и новых имен должно быть одинаковым.")
        return

    # rename files
    for file, new_name in zip(csv_files, asin_list):
        new_file_path = os.path.join(folder_path, new_name)
        os.rename(file, new_file_path + '.csv')
        print(f"Файл {file} переименован в {new_name}.")


def load_sales(asin_list=None, log_pas_file='logins.txt', save_directory=None):
    """
       Renaming files in destination folder, which contain keyword in file name .

        Args:
            asin_list (list): list of target asins
            log_pas_file (string): path to file with logins and passwords
            save_directory(string): path to save result files


        Returns:
            None
    """
    # Path to the extension file .crx
    extension_path = 'helium.crx'

    # get login and password from file
    with open(log_pas_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                parts = line.split(':')
                login_text = parts[0].strip()
                password_text = parts[1].strip()

    global human_inter

    # Creating a ChromeOptions Object and specifying the path to the extension
    chrome_options = Options()
    chrome_options.add_extension(extension_path)
    if save_directory is not None:
        download_dir = save_directory
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False
        }
        chrome_options.add_experimental_option("prefs", prefs)

    # Chrome Driver Initialization
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://members.helium10.com/user/signup?type=chrome-extension')
    handles = driver.window_handles
    driver.switch_to.window(handles[1])
    driver.close()
    driver.switch_to.window(handles[0])

    # Get to signup page
    wait = WebDriverWait(driver, 10)
    element = driver.find_element(By.CSS_SELECTOR, "a.signup-form-bottom__link")
    element.click()

    # Enter login
    login = driver.find_element(By.CSS_SELECTOR, "input#loginform-email")
    login.send_keys(login_text)
    wait = WebDriverWait(driver, 10)

    # Enter password
    password = driver.find_element(By.CSS_SELECTOR, "input#loginform-password")
    password.send_keys(password_text)
    wait = WebDriverWait(driver, 10)

    # get to the main page
    element = driver.find_element(By.CSS_SELECTOR, "button.btn.btn-secondary.btn-block")
    element.click()
    time.sleep(random.randint(5, 10))
    human_inter = True

    for asin in asin_list:
        # For each asin get data from service

        driver.get('https://www.amazon.com/dp/' + asin)
        # wait for extension login
        while human_inter:
            time.sleep(1)
        wait = WebDriverWait(driver, 20)  # Maximum wait time in seconds

        # after login get data from extension
        try:
            open_graph = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc-ga-dRe")))
            time.sleep(random.randint(1, 3))
        except Exception as exp:
            driver.refresh()
            wait = WebDriverWait(driver, 20)  # Maximum wait time in seconds
            open_graph = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc-ga-dRe")))
            time.sleep(random.randint(1, 3))
        # open_graph = driver.find_element(By.CSS_SELECTOR, "div.sc-ga-dRe")

        try:
            open_graph.click()
            time.sleep(random.randint(1, 3))
        except Exception as exp:
            driver.refresh()
            wait = WebDriverWait(driver, 20)  # Maximum wait time in seconds
            open_graph = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc-ga-dRe")))
            time.sleep(random.randint(1, 3))
            open_graph.click()

        # change date to all time
        all_time = driver.find_element(By.XPATH, "//li[contains(text(), 'All Time')]")
        all_time.click()
        time.sleep(random.randint(1, 3))

        # open chart menu
        menu = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="View chart menu"]')))
        menu.click()
        time.sleep(random.randint(1, 3))

        # download graph in csv
        download = driver.find_element(By.XPATH, "//li[text()='Download CSV']")
        download.click()
        time.sleep(random.randint(5, 10))
        _rename_files_in_folder(folder_path=os.path.join(os.path.expanduser("~"), "Downloads"), asin_list=[asin])


def load_searches(key_list=None, log_pas_file='logins.txt', save_directory=None):
    """
       Renaming files in destination folder, which contain keyword in file name .

        Args:
            key_list (list): list of target keywords
            log_pas_file (string): path to file with logins and passwords
            save_directory(string): path to save result files


        Returns:
            None
    """
    # Get to signup page
    with open(log_pas_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                parts = line.split(':')
                login_text = parts[0].strip()
                password_text = parts[1].strip()

    global human_inter
    human_inter = True

    # Creating a ChromeOptions object and specifying the path to the extension
    chrome_options = Options()
    if save_directory is not None:
        download_dir = save_directory
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False
        }
        chrome_options.add_experimental_option("prefs", prefs)

    # Chrome Driver Initialization
    driver = webdriver.Chrome(options=chrome_options)

    # Get to signup page
    driver.get('https://members.helium10.com/user/signin')

    # wait = WebDriverWait(driver, 10)
    # element = driver.find_element(By.CSS_SELECTOR, "a.signup-form-bottom__link")
    # element.click()

    # Enter login
    login = driver.find_element(By.CSS_SELECTOR, "input#loginform-email")
    login.send_keys(login_text)
    wait = WebDriverWait(driver, 10)

    # Enter password
    password = driver.find_element(By.CSS_SELECTOR, "input#loginform-password")
    password.send_keys(password_text)
    wait = WebDriverWait(driver, 10)

    # #  wait for capcha solving
    # while human_inter:
    #     time.sleep(1)

    # get to the main page
    element = driver.find_element(By.CSS_SELECTOR, "button.btn.btn-secondary.btn-block")
    element.click()
    #  wait for capcha solving
    while human_inter:
        time.sleep(1)
    # time.sleep(random.randint(5, 10))

    for num, key in enumerate(key_list):

        if num > 0:
            # if it isn't the first key, close graph,scroll up and remove previous key
            time.sleep(1)
            element = driver.find_element(By.XPATH, "//button[@data-testid='close-button']")
            element.click()
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            driver.find_element(By.XPATH, "//div[@data-testid='remove-button']").click()
        else:
            # get to proper account id
            driver.get('https://members.helium10.com/magnet?accountId=1545867146')

        wait = WebDriverWait(driver, 30)  # Maximum wait time in seconds
        try:
            # get data about keyword
            enter_key = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder=\"Enter a keyword\"]")))
            enter_key.send_keys(key)
            time.sleep(random.randint(1, 4))
            element = driver.find_element(By.XPATH, "//button[contains(text(), 'Get Keywords')]")
            element.click()
            time.sleep(random.randint(1, 4))
            try:
                button = driver.find_element(By.XPATH, "//button[contains(text(), 'Run New Search')]")
                button.click()
            except Exception as exp:
                time.sleep(20)
                pass
        except Exception as exp:
            driver.refresh()
            wait = WebDriverWait(driver, 20)  # Maximum wait time in seconds
            enter_key = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder=\"Enter a keyword\"]")), )
            enter_key.send_keys(key)
            time.sleep(random.randint(1, 4))
            element = driver.find_element(By.XPATH, "//button[contains(text(), 'Get Keywords')]")
            element.click()
            time.sleep(random.randint(1, 4))
            try:
                button = driver.find_element(By.XPATH, "//button[contains(text(), 'Run New Search')]")
                button.click()
            except Exception as exp:
                pass
        # open_graph = driver.find_element(By.CSS_SELECTOR, "div.sc-ga-dRe")
        wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="re-container"]/div[2]/div[1]/div/div/div[3]/div/div['
                                                      '1]/div[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[1]/button')))
        try:
            graph = driver.find_element(By.XPATH, '//*[@id="re-container"]/div[2]/div[1]/div/div/div[3]/div/div['
                                                  '1]/div[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[1]/button')
            element = driver.find_element(By.XPATH, "//div[text()='Keyword Search Summary']")
            driver.execute_script("arguments[0].scrollIntoView();", element)
            time.sleep(1)
            graph.click()
            time.sleep(random.randint(1, 3))
        except Exception as exp:

            graph = driver.find_element(By.XPATH, '//*[@id="re-container"]/div[2]/div[1]/div/div/div[3]/div/div['
                                                  '1]/div[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[1]/button')
            element = driver.find_element(By.XPATH, "//div[text()='Keyword Search Summary']")
            driver.execute_script("arguments[0].scrollIntoView();", element)
            time.sleep(1)
            graph.click()
            time.sleep(random.randint(1, 3))
        # show table of options
        driver.find_element(By.XPATH, "//span[contains(text(), '1 Year')]").click()
        # click on last option
        driver.find_element(By.XPATH, "//div[contains(text(), 'All time')]").click()
        time.sleep(random.randint(1, 3))

        menu = driver.find_element(By.CSS_SELECTOR, 'g.highcharts-no-tooltip')
        menu.click()
        # time.sleep(random.randint(1, 3))

        download = driver.find_element(By.XPATH, "//li[text()='Download CSV']")
        download.click()
        time.sleep(random.randint(5, 10))
        _rename_files_in_folder(folder_path=os.path.join(os.path.expanduser("~"), "Downloads"), asin_list=[key])
    print('Finished')
    # _rename_files_in_folder(folder_path=os.path.join(os.path.expanduser("~"), "Downloads"),asin_list=asin_list)

# element = driver.find_element(By.CSS_SELECTOR, '#h10-page-widget > div')
#

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
