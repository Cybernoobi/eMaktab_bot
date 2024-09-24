import json


class CookiesManager:
    def __init__(self, login: str, key: dict = None):
        self.login = login
        self.key = key

    def save_cookie(self):
        if self.key is not None:
            with open(f'./utils/cookies/{self.login}.json', mode='w') as file:
                json.dump(self.key, file, indent=4)

    def get_cookie(self) -> dict:
        with open(f'./utils/cookies/{self.login}.json', mode='r') as file:
            return json.load(file)
