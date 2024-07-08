from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from bs4 import BeautifulSoup
from pprint import pprint

import re

# local
from utils.database.requests import get_emaktab

# links
LOGIN_URL = 'https://login.emaktab.uz/'
BASE_URL = 'https://emaktab.uz/'


# Click for quarter
async def click_quarter(quarter, driver):
    try:
        # Находим элементы четвертей
        quarters = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'sF2Bq')))
        quarter_index = int(quarter) - 1

        # Кликаем на нужную четверть
        quarters[quarter_index].click()

    except Exception as e:
        print(f'Ошибка при клике на четверть: {e}')


# Driver
async def connect_driver(url: str):
    from sys import platform
    import os

    # Driver options
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--incognito')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    if platform == 'win32':
        os.environ['PATH'] += os.pathsep + r'.\drivers\chromewindows.exe'
    elif platform in ['linux', 'linux2']:
        os.environ['PATH'] += os.pathsep + r'./drivers/chromelinux'

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    return driver


# Auto site login
async def site_login(driver: webdriver, login: str, password: str):
    wait = WebDriverWait(driver, 0)

    username_field = wait.until(EC.presence_of_element_located((By.NAME, 'login')))
    password_field = wait.until(EC.presence_of_element_located((By.NAME, 'password')))

    username_field.send_keys(login)
    password_field.send_keys(password)

    # Click registration button
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[data-test-id="login-button"]'))).click()

    # Incorrect password or login
    try:
        error_message = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.message'))).text
        return 'Incorrect password'
    except TimeoutException:
        try:
            wait.until(EC.url_to_be(BASE_URL + 'userfeed'))
            return driver
        except Exception:
            return 'Error 404'


async def emaktab_connect(user_id: int, login: str, password: str):
    browser = await connect_driver(LOGIN_URL)
    driver = await site_login(browser, login, password)

    if driver == 'Error 404':
        return 'Error 404'

    elif driver == 'Incorrect password':
        return ('[RU] Проверьте правильность введенного логина или восстановите его на сайте\n'
                '[UZ] Kiritilgan loginning to\'g\'riligini tekshiring yoki uni saytda tiklang')

    else:
        if await get_emaktab(user_id, login, password, added=True) == 'success':
            return ('[RU] Вы успешно вошли в аккаунт\n'
                    '[UZ] Siz hisob qaydnomasiga muvaffaqiyatli kirdingiz')
        else:
            return 'Error'


async def emaktab_get_mark(login: str, password: str):
    browser = await connect_driver(LOGIN_URL)
    driver = await site_login(browser, login, password)

    if driver == 'Error 404':
        return 'Error 404'

    elif driver == 'Incorrect password':
        return 'Incorrect password'

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
                output += f'\nОценки за {date}:\n'
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


async def emaktab_get_average_score(login: str, password: str, quart: int):
    browser = await connect_driver(LOGIN_URL)
    driver = await site_login(browser, login, password)

    if driver == 'Error 404':
        return 'Error 404'

    elif driver == 'Incorrect password':
        return 'Incorrect password'

    else:
        try:
            # Переходим на страницу с оценками
            driver.get(BASE_URL + 'marks')

            # Кликаем на нужную четверть
            wait = WebDriverWait(driver, 15)
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.XZC4H[data-test-id="tab-period"]'))).click()
            await click_quarter(quart, driver)

            # Ожидаем загрузки таблицы с оценками
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'Tamh1')))

            # Парсим страницу с оценками
            html = BeautifulSoup(driver.page_source, "html.parser")
            wrapper = html.select('table.Tamh1 tbody tr')

            results = []
            output = ""

            if quart <= 4:
                for subject in wrapper:
                    subject_name = subject.select_one('.c8D3G').text.strip()
                    marks = [mark.text.strip() for mark in subject.select('[data-test-id^="work_mark"]')]
                    average_score = subject.select_one('td:nth-of-type(3)').text.strip()
                    quarter_score = subject.select_one('td:nth-of-type(4)').text.strip()

                    results.append({
                        'subject': subject_name,
                        'marks': marks,
                        'average_score': average_score,
                        'quarter_score': quarter_score
                    })

                for result in results:
                    marks_str = ', '.join(result['marks'])
                    output += (
                        f"\n{result['subject']}: Ср. балл: {result['average_score']} | Четверть: {result['quarter_score']}\n"
                    # {marks_str} |
                    )

                return output
            else:
                # Проход по каждой строке с данными предметов
                for subject in wrapper:
                    subject_name = subject.select_one('.c8D3G').text.strip() if subject.select_one(
                        '.c8D3G') else 'Нет названия'

                    # Извлекаем оценки за четверти и годовую оценку с проверкой на наличие
                    first_quarter = subject.select_one('[data-test-id*="final-mark_period-"][data-test-id$="_0"]')
                    first_quarter = first_quarter.text.strip() if first_quarter else "-"

                    second_quarter = subject.select_one('[data-test-id*="final-mark_period-"][data-test-id$="_1"]')
                    second_quarter = second_quarter.text.strip() if second_quarter else "-"

                    third_quarter = subject.select_one('[data-test-id*="final-mark_period-"][data-test-id$="_2"]')
                    third_quarter = third_quarter.text.strip() if third_quarter else "-"

                    fourth_quarter = subject.select_one('[data-test-id*="final-mark_period-"][data-test-id$="_3"]')
                    fourth_quarter = fourth_quarter.text.strip() if fourth_quarter else "-"

                    year_mark = subject.select_one('[data-test-id^="final-year"]')
                    year_mark = year_mark.text.strip() if year_mark else "-"

                    exam_mark_tag = subject.select_one('[data-test-id^="final-exam"]')
                    exam_mark = exam_mark_tag.text.strip() if exam_mark_tag else "-"

                    final_mark = subject.select_one('[data-test-id^="final-final"]')
                    final_mark = final_mark.text.strip() if final_mark else "-"

                    # Формируем строку для текущего предмета
                    output += f"""
{subject_name}: 
    1 четверть: {first_quarter}
    2 четверть: {second_quarter}
    3 четверть: {third_quarter}
    4 четверть: {fourth_quarter}
    За год: {year_mark}
    Экзамен: {exam_mark}
    Итог: {final_mark}
"""

            return output

        except Exception as e:
            return f'Ошибка: {e},\n{e.__class__},\n{e.args}'

        finally:
            driver.quit()
