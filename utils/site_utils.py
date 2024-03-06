from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
from pprint import pprint

import re

# local
from utils.database import add_emaktab

# links
LOGIN_URL = 'https://login.emaktab.uz/'
BASE_URL = 'https://emaktab.uz/'


# Driver
async def connect_driver(url: str):
    import os

    # Driver options
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    os.environ['PATH'] += os.pathsep + r'.\msedgedriver.exe'
    driver = webdriver.Edge(options=options)
    driver.get(url)
    return driver


async def site_login(driver: webdriver, login: str, password: str):
    # Enter your data
    wait = WebDriverWait(driver, 5)

    username_field = wait.until(EC.presence_of_element_located((By.NAME, 'login')))
    password_field = wait.until(EC.presence_of_element_located((By.NAME, 'password')))

    username_field.send_keys(login)
    password_field.send_keys(password)

    # Click registration button
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[data-test-id="login-button"]'))).click()

    # Incorrect password or login
    try:
        error_message = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.message'))).text
        print('Incorrect password')
        return 'Incorrect password'
    except:
        pass

    # Ждем загрузки страницы после входа
    try:
        wait.until(EC.url_to_be(BASE_URL + 'userfeed'))
        return driver
    except:
        print('Error 404')
        return 'Error 404'


async def emaktab_connect(db_name: str, user_id: int, login: str, password: str):
    browser = await connect_driver(LOGIN_URL)
    driver = await site_login(browser, login, password)

    if driver == 'Error 404':
        return 'Error 404'

    elif driver == 'Incorrect password':
        return ('[RU] Проверьте правильность введенного логина или восстановите его на сайте\n'
                '[UZ] Kiritilgan loginning to\'g\'riligini tekshiring yoki uni saytda tiklang')

    else:
        await add_emaktab(db_name, user_id, login, password)
        return ('[RU] Вы успешно вошли в аккаунт\n'
                '[UZ] Siz hisob qaydnomasiga muvaffaqiyatli kirdingiz')


async def emaktab_get_mark(login: str, password: str):
    browser = await connect_driver(LOGIN_URL)
    driver = await site_login(browser, login, password)

    if driver == 'Error 404':
        return 'Error 404'

    elif driver == 'Incorrect password':
        return ('[RU] Проверьте правильность введенного логина или восстановите его на сайте\n'
                '[UZ] Kiritilgan loginning to\'g\'riligini tekshiring yoki uni saytda tiklang')

    else:

        # Ждем загрузки страницы после входа
        try:
            html = BeautifulSoup(driver.page_source, "html.parser")
            wrapper = html.find('div', class_='O4Y1L')
            marks_objects = wrapper.find_all('div', class_='NmbeA')

            output = ""

            # Проходим по каждому блоку
            for block in marks_objects:
                date = block.find(class_='H1xuJ').text.strip()
                output += f'Оценки за {date}:\n'
                marks = block.find_all(class_='Wgxhi')
                for mark in marks:
                    mark_subject = re.sub(r'[^\w\s\']', '', mark.find(class_='qZR20').text.strip())
                    mark_value = re.sub(r'[^\w\s\']', '', mark.find(class_='h26OT').text.strip())
                    mark_description = re.sub(r'[^\w\s\']', '', mark.find(class_='UDZhX').text.strip())
                    output += f"  {mark_subject}: {mark_value} ({mark_description})\n"

            return output


        except Exception as e:
            return f'Ошибка: {e},\n{e.__class__},\n{e.args}'
        finally:
            driver.quit()

