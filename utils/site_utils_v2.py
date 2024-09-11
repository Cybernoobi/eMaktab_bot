# Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# bs4 and re
from bs4 import BeautifulSoup
import re

# local
from utils.database.requests import get_emaktab

def browser_connect():
    from sys import platform
    import os

    # Driver options
    options = Options()
    # options.add_argument('--headless')
    options.add_argument('--incognito')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    if platform == 'win32':
        os.environ['PATH'] += r'.\drivers\chromewindows.exe'
    elif platform in ['linux', 'linux2']:
        os.environ['PATH'] += r'./drivers/chromelinux'

    driver = webdriver.Chrome(options=options)

    return driver


def site_log(func, login: str = None, password: str = None, driver: webdriver.Chrome = None) -> str:
    driver.get('https://login.emaktab.uz/')

    wait = WebDriverWait(driver, 3)

    login_form = wait.until(EC.presence_of_element_located((By.NAME, 'login')))
    password_form = wait.until(EC.presence_of_element_located((By.NAME, 'password')))

    login_form.send_keys(login)
    password_form.send_keys(password)

    driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')

    if wait.until(EC.url_changes('https://emaktab.uz/userfeed')):
        func()
    else:
        return 'error'


class EmaktabManager:
    def __init__(self, user_id: int, login: str, password: str):
        self.user_id = user_id
        self.login = login
        self.password = password
        self.driver = browser_connect()

    def close_driver(self):
        self.driver.close()
        self.driver.quit()

    def site_login(self, func) -> str:
        self.driver.get('https://login.emaktab.uz/')
        wait = WebDriverWait(self.driver, 10)

        login_form = wait.until(EC.presence_of_element_located((By.NAME, 'login')))
        password_form = wait.until(EC.presence_of_element_located((By.NAME, 'password')))

        login_form.send_keys(self.login)
        password_form.send_keys(self.password)

        self.driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()

        result = None
        try:
            if wait.until(EC.url_changes('https://emaktab.uz/userfeed')):
                result = func(self.driver)
        except TimeoutException:
            result = 'error'

        self.driver.close()
        return result

    def emaktab_connect(self, added: bool = False):
        @self.site_login
        def _ret():
            if added is True:
                if get_emaktab(self.user_id, self.login, self.password, added=True) == 'success':
                    return 'success'
                else:
                    return 'error'
            else:
                return 'error'

    def emaktab_get_mark(self):
        @self.site_login
        def get_marks():
            try:
                html = BeautifulSoup(self.driver.page_source, "html.parser")
                wrapper = html.find('div', class_='O4Y1L')
                marks_objects = wrapper.find_all('div', class_='NmbeA')

                output = ""

                # Проходим по каждому блоку
                for block in marks_objects:
                    date = block.find(class_='H1xuJ').text.strip()
                    output += f'\nОценки за {date}:\n'
                    marks = block.find_all(class_='Wgxhi')
                    for mark in marks:
                        mark_subject = re.sub(r'[^\w\s\']', '', mark.find(class_='qZR20').text.strip())
                        mark_value = re.sub(r'[^\w\s\']', '', mark.find(class_='h26OT').text.strip())
                        mark_description = re.sub(r'[^\w\s\']', '', mark.find(class_='UDZhX').text.strip())
                        output += f"  {mark_subject}: {mark_value} ({mark_description})\n"

                return output
            except Exception as e:
                return 'error', e, 'site_utils_v2'

    def coks(self):
        @self.site_login
        def __coks(driver):
            from pprint import pprint
            pprint(driver.get_cookies())
