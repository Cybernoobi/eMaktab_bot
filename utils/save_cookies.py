class CookiesManager:
    def __init__(self, login: str, key: dict, lang: dict):
        self.key = key
        self.login = login
        self.lang = lang

    def save(self):
        try:
            with open(f'./utils/cookies/{self.login}/key.txt', mode='w') as file:
                file.write(str(self.key))

            with open(f'./utils/cookies/{self.login}/lang.txt', mode='w') as file:
                file.write(str(self.lang))
        except FileNotFoundError:
            import os
            os.mkdir(f'./utils/cookies/{self.login}')

            with open(f'./utils/cookies/{self.login}/key.txt', mode='w') as file:
                file.write(str(self.key))

            with open(f'./utils/cookies/{self.login}/lang.txt', mode='w') as file:
                file.write(str(self.lang))

        return True

    def get_cookies(self, cook: str = 'all') -> list:
        result = []
        if cook == 'all':
            with open(f'./utils/cookies/{self.login}/key.txt', mode='r') as file:
                result.append(dict(file.json()))
            with open(f'./utils/cookies/{self.login}/lang.txt', mode='r') as file:
                result.append(dict(file.json()))

        elif cook == 'key':
            with open(f'./utils/cookies/{self.login}/key.txt', mode='r') as file:
                result.append(dict(file.read()))

        elif cook == 'lang':
            with open(f'./utils/cookies/{self.login}/lang.txt', mode='r') as file:
                result.append(dict(file.read()))

        return result
