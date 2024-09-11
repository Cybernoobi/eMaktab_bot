import json


class CookiesManager:
    def __init__(self, login: str, key: dict = None):
        self.key = key
        self.login = login

    def save(self):
        if self.key is not None:
            with open(f'./utils/cookies/{self.login}.json', mode='w') as file:
                json.dump(self.key, file, indent=4)

    def get_cookie(self) -> list:
        with open(f'./utils/cookies/{self.login}.json', mode='r') as file:
            return json.load(file)
