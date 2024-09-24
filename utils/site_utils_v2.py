# Selenium
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# bs4 and re
from bs4 import BeautifulSoup
import re

# local
from utils.database.requests import get_emaktab
from utils.other_utils import CookiesManager
from utils.config import DEBUG
from utils import (IncorrectLoginOrPasswordError, NotSubscribedError,
                   TemporaryPasswordError, UserDataIsNoneError, CaptchaError)


def browser_connect():
    from sys import platform
    import os

    # Driver options
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)

    if DEBUG is False:
        options.add_argument('--headless')

    options.add_argument('--no-sandbox')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-dev-shm-usage')

    if platform == 'win32':
        os.environ['PATH'] += r'.\drivers\chromewindows.exe'
    elif platform in ['linux', 'linux2']:
        os.environ['PATH'] += r'./drivers/chromelinux'

    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_JSON;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Object;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            '''})

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
    def __init__(self, user_id: int = None, login: str = None, password: str = None):
        self.user_id = user_id
        self.login = login
        self.password = password

        self.driver = browser_connect()
        self.BASE_URL = 'https://emaktab.uz/'
        self.LOGIN_URL = 'https://login.emaktab.uz/'

    def close_driver(self):
        self.driver.close()
        self.driver.quit()

    def first_login(self):
        if self.user_id is None and self.login is None and self.password is None:
            raise UserDataIsNoneError("Нет данных для входа")

        self.driver.get(self.LOGIN_URL)
        wait = WebDriverWait(self.driver, 25)

        login_form = wait.until(EC.presence_of_element_located((By.NAME, 'login')))
        password_form = wait.until(EC.presence_of_element_located((By.NAME, 'password')))

        login_form.send_keys(self.login)
        password_form.send_keys(self.password)

        self.driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()

        soup = BeautifulSoup(self.driver.page_source, 'html.parser').find(name='input',
                                                                          class_='input_captcha-validation')

        if soup is not None:
            import nopecha
            text = nopecha.Recognition.solve(
                type='textcaptcha',
                image_urls=[self.driver.find_element(
                    By.CSS_SELECTOR, 'img[alt="captcha image"]').get_attribute('src')],
            )

            try:
                self.driver.find_element(By.NAME, 'Captcha.Input').send_keys(text['data'][0])
                self.driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()
            except KeyError:
                raise CaptchaError(f"Каптча не было пройдена - error:{text['error']} text:{text['message']}")

        try:
            error = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.message')))

            if error is not None:
                if error.text.strip() in ['Parol yoki login notoʻgʻri koʻrsatilgan. Qaytadan urinib koʻring.',
                                          'Неправильно указан пароль или логин. Попробуйте еще раз.']:
                    raise IncorrectLoginOrPasswordError("Введен неправильный логин или пароль")
                else:
                    return error.text

        except Exception as e:
            return e

        CookiesManager(self.login, self.driver.get_cookie('UZDnevnikAuth_a')).save_cookie()

        if wait.until(EC.url_to_be(self.BASE_URL + 'userfeed')):
            return True

        elif wait.until(EC.url_to_be(self.BASE_URL + 'billing')):
            raise NotSubscribedError("Отсутствует базовая подписка eMaktab")

        elif re.search(r'password\?login=.*&token=.*', self.driver.current_url):
            print('start')

            new_password = 'uz_emaktab_robot'

            wait.until(EC.presence_of_element_located((By.NAME, 'Password'))).send_keys(new_password)
            wait.until(EC.presence_of_element_located((By.NAME, 'RepeatedPassword'))).send_keys(new_password)

            self.driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()

            raise TemporaryPasswordError(f"Введён временный пароль\nНовый пароль: {new_password}")

    def site_login(self, func) -> str:
        self.driver.get(self.LOGIN_URL)

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

    def test(self):
        @self.site_login
        def _info():
            print(self.driver.current_url)
