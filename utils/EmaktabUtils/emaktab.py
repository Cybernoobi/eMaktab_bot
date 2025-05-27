from pprint import pprint

from aiohttp import ClientSession, FormData

BASE_URL = "https://emaktab.uz"

class EmaktabAPI:
    def __init__(self, auth_token: str = None, base_url: str = BASE_URL):
        self.BASE_URL = base_url
        self.API_URL = base_url + "/api"

        self.session = ClientSession(base_url=BASE_URL)
        self.auth_token = auth_token

    async def auth(self, login: str, password: str):
        self.session._base_url = None
        auth_data = FormData()
        auth_data.add_field("login", login)
        auth_data.add_field("password", password)

        async with self.session.post(f"https://login.{BASE_URL.split('//')[1]}", data=auth_data) as response:
            pprint(await response.text())

        await self.session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()