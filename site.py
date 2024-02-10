import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support import expected_conditions as EC

# local
from database import add_emaktab

LOGIN_URL = 'https://login.emaktab.uz/'
BASE_URL = 'https://emaktab.uz/'


def emaktab_connect(login: str, password: str, user_id: int):
    # driver path
    os.environ['PATH'] += os.pathsep + r'.\msedgedriver.exe'

    # Options
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Edge(options=options)

    driver.get(LOGIN_URL)

    # Введите свои данные
    wait = WebDriverWait(driver, 5)

    username_field = wait.until(EC.presence_of_element_located((By.NAME, 'login')))
    password_field = wait.until(EC.presence_of_element_located((By.NAME, 'password')))

    username_field.send_keys(login)
    password_field.send_keys(password)

    # Нажмите кнопку регистрации
    submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[data-test-id="login-button"]'))).click()

    # Проверяем наличие сообщения об ошибке после нажатия на кнопку "Submit"
    try:
        error_message = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.message'))).text
        return 'Проверьте правильность введенного логина или восстановите его на сайте'
    except:
        pass

    # Ждем загрузки страницы после входа
    try:
        wait.until(EC.url_to_be(f'{BASE_URL}userfeed'))
        
        add_emaktab(DATABASE_NAME, user_id, login, password)
        
        return 'Вы успешно вошли в аккаунт'
    except:
        return 'Не удалось загрузить страницу после входа'
    finally:
        driver.quit()
