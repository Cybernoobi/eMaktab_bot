import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
from pprint import pprint

# local
from utils.database import add_emaktab

# links
LOGIN_URL = 'https://login.emaktab.uz/'
BASE_URL = 'https://emaktab.uz/'

# Driver options
options = Options()


# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-dev-shm-usage')

# Driver
def connect_driver(url: str):
    os.environ['PATH'] += os.pathsep + r'.\msedgedriver.exe'
    driver = webdriver.Edge(options=options)
    driver.get(url)
    return driver


async def emaktab_connect(db_name: str, user_id: int, login: str, password: str):
    driver = connect_driver(LOGIN_URL)

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
        return ('[RU] Проверьте правильность введенного логина или восстановите его на сайте\n'
                '[UZ] Kiritilgan loginning to\'g\'riligini tekshiring yoki uni saytda tiklang')
    except:
        pass

    # Ждем загрузки страницы после входа
    try:
        wait.until(EC.url_to_be(BASE_URL + 'userfeed'))

        await add_emaktab(db_name, user_id, login, password)

        return ('[RU] Вы успешно вошли в аккаунт\n'
                '[UZ] Siz hisob qaydnomasiga muvaffaqiyatli kirdingiz')
    except:
        return 'Не удалось загрузить страницу после входа'
    finally:
        driver.quit()


async def emaktab_get_mark(login: str, password: str):
    driver = connect_driver(LOGIN_URL)

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
        return 'Incorrect login or password'
    except:
        pass

    # Ждем загрузки страницы после входа
    try:
        wait.until(EC.url_to_be(BASE_URL + 'userfeed'))

        html = BeautifulSoup(driver.page_source, "html.parser")
        wrapper = html.find('div', class_='O4Y1L')
        marks_objects = wrapper.find_all('div', class_='NmbeA')

        result = []

        for mark_obj in marks_objects:
            date = mark_obj.find('div', class_='H1xuJ')
            marks = mark_obj.find_all('div', class_='Wgxhi')
            for mark in marks:
                subject = mark.find('div', class_='qZR20').text
                subject_mark = mark.find('div', class_='h26OT ceyZF').text
                subject_data = mark.find('div', class_='UDZhX').text
                print(f'''
                Предмет: {subject},
                Оценка: {subject_mark},
                Выставлено за: {subject_data}''')


    except Exception as e:
        return f'Ошибка: {e},\n{e.__class__},\n{e.args}'
    finally:
        driver.quit()
