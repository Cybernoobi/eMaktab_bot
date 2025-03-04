import re
import os
import json
from enum import Enum


def validate_username(username):
    pattern = r'^[A-Za-z][A-Za-z0-9._-]{4,18}[A-Za-z0-9_-]$'
    # Проверяем, что строка соответствует всем критериям
    if re.match(pattern, username):
        return True
    else:
        return False


def load_message(msg: str, lang: str):
    path = f'./utils/messages/{msg}.json'

    if os.path.isfile(path):
        with open(path, mode='r', encoding='UTF-8') as file:
            res: dict = json.load(file)

        return res[lang]

    else:
        raise FileNotFoundError("Message file not found")


class CookiesManager:
    def __init__(self, login: str):
        self.login = login

    def save_cookie(self, keys: list[dict]):
        if keys is not None:
            # Собираем все куки в список
            cookies = []
            for key in keys:
                cookies.append(key)

            # Сохраняем все куки в один файл
            with open(f'./utils/cookies/{self.login}.json', mode='w', encoding='UTF-8') as file:
                json.dump(cookies, file, indent=4)

    def get_cookies(self, lang: str) -> list[dict]:
        path = f'./utils/cookies/{self.login}.json'

        if os.path.isfile(path):
            with open(path, mode='r', encoding='UTF-8') as file:
                res: list[dict] = json.load(file)

            for cookie in res:
                if cookie["name"] == "Dnevnik_localization":
                    cookie["value"] = lang
                else:
                    res.append({
                        "name": "Dnevnik_localization",
                        "value": lang
                        # "sameSite": "None"
                    })

            return res

        else:
            raise FileNotFoundError("Cookies file not found")

    def delete_cookie(self):
        try:
            os.remove(f'./utils/cookies/{self.login}.json')
        except FileNotFoundError:
            raise FileNotFoundError("Cookies file not found")


class MyFilter(str, Enum):
    TELEGRAM = 'tg'
    EMAKTAB = 'em'
    USER_SETTINGS = 'us'


class Langs(str, Enum):
    RU = 'ru-RU'
    UZ = 'uz-Latn-UZ'
