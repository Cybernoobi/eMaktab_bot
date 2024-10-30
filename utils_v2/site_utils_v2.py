# Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException

# misc
import re
import random
from logging import *

# local
from utils.database.requests import get_emaktab
from utils.other_utils import CookiesManager
from utils.config import DEBUG
from utils import (IncorrectLoginOrPasswordError, NotSubscribedError, IncorrectUserCookieError,
                   TemporaryPasswordError, UserDataIsNoneError, CaptchaError)


async def browser_connect() -> webdriver.Chrome:
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


class EmaktabManager:
    def __init__(self, user_id: int = None, login: str = None, password: str = None):
        self.user_id = user_id
        self.login = login
        self.password = password

        self.driver = None #browser_connect()
        self.BASE_URL = 'https://emaktab.uz/'
        self.LOGIN_URL = 'https://login.emaktab.uz/'

    async def init(self):
        self.driver = await browser_connect()

    async def wait(self, seconds: [int, float] = 5) -> WebDriverWait:
        return WebDriverWait(self.driver, seconds)

    async def close_driver(self):
        self.driver.close()
        self.driver.quit()

    async def first_login(self, func=None):
        if self.user_id is None and self.login is None and self.password is None:
            raise UserDataIsNoneError("Нет данных для входа")

        info(f'start login {self.login}')
        self.driver.get(self.LOGIN_URL)

        wait = await self.wait()

        login_form = wait.until(EC.presence_of_element_located((By.NAME, 'login')))
        password_form = wait.until(EC.presence_of_element_located((By.NAME, 'password')))

        login_form.send_keys(self.login)
        password_form.send_keys(self.password)

        self.driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()

        try:
            captcha = (await self.wait(0.15)).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[class="input_captcha-validation"]')))

            if captcha is not None:
                if captcha.is_displayed() is True:
                    info('start auto-captcha')
                    import nopecha
                    text = nopecha.Recognition.solve(
                        type='textcaptcha',
                        image_urls=[self.driver.find_element(
                            By.CSS_SELECTOR, 'img[alt="captcha image"]').get_attribute('src')],
                    )

                    try:
                        self.driver.find_element(By.NAME, 'Captcha.Input').send_keys(text['data'][0])
                        self.driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()
                        info('end auto-captcha')
                    except KeyError:
                        warning('auto-captcha failed')
                        raise CaptchaError(f"Каптча не было пройдена - error:{text['error']} text:{text['message']}")
                    except ElementNotInteractableException:
                        pass

        except TimeoutException:
            pass

        try:
            error = (await self.wait(0.3)).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.message')))

            if error is not None:
                if error.text.strip() in ['Parol yoki login notoʻgʻri koʻrsatilgan. Qaytadan urinib koʻring.',
                                          'Неправильно указан пароль или логин. Попробуйте еще раз.']:
                    info('incorrect password')
                    raise IncorrectLoginOrPasswordError("Введен неправильный логин или пароль")
                else:
                    warning(error.text)
                    raise Exception("eMaktabError")

        except TimeoutException:
            pass

        if re.search(r'password\?login=.*&token=.*', self.driver.current_url) is not None:
            new_password = f'{self.login}_{random.randint(1000, 9999)}'

            wait.until(EC.presence_of_element_located((By.NAME, 'Password'))).send_keys(new_password)
            wait.until(EC.presence_of_element_located((By.NAME, 'RepeatedPassword'))).send_keys(new_password)

            self.driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]').click()

            raise TemporaryPasswordError(f"Введён временный пароль\nНовый пароль: {new_password}")

        elif wait.until(EC.url_to_be(self.BASE_URL + 'userfeed')):
            CookiesManager(self.login).save_cookie(self.driver.get_cookies())
            if func:
                await func()
            return True

        elif wait.until(EC.url_to_be(self.BASE_URL + 'billing')):
            raise NotSubscribedError("Отсутствует базовая подписка eMaktab")

    async def site_login(self, func=None):
        self.driver.get(self.BASE_URL + 'about')

        try:
            cookies = CookiesManager(self.login).get_cookies('ru-RU')
        except FileNotFoundError:
            await self.first_login()

        for cookie in cookies:
            self.driver.add_cookie(cookie)

        self.driver.get(self.BASE_URL)

        try:
            if (await self.wait(0.5)).until(EC.url_to_be(self.BASE_URL + 'userfeed')):
                await func()
        except TimeoutException:
            if func:
                await self.first_login(func)

    @site_login
    async def get_marks(self):
        print(123)
        # self.driver.get(self.BASE_URL)