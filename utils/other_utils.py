import json
import logging


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
            with open(f'./utils/cookies/{self.login}.json', mode='w') as file:
                json.dump(cookies, file, indent=4)

    def get_cookies(self, lang: str) -> list[dict]:
        with open(f'./utils/cookies/{self.login}.json', mode='r') as file:
            res = json.load(file)

        for cookie in res:
            if cookie["name"] == "Dnevnik_localization":
                cookie["value"] = lang

        return res


def start_logging(level: logging = logging.INFO):
    logging.basicConfig(filename='logs/debug.log',
                        level=level,
                        format='%(asctime)s - %(message)s')
