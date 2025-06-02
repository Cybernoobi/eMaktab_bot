from pprint import pprint

import ujson
from aiohttp import ClientSession, FormData

from schemas import EUserSchema
from .utils import check_url

BASE_URL: str = "emaktab.uz"


class Client:
    def __init__(self, login: str = None, password: str = None, base_url: str = BASE_URL):
        self.BASE_URL = check_url(base_url)
        self.session = ClientSession(base_url=self.BASE_URL)

        self.login = login
        self.password = password
        self.user: EUserSchema | None = None

    async def auth(self):
        self.session._base_url = None
        auth_data = FormData()
        auth_data.add_field("login", self.login)
        auth_data.add_field("password", self.password)

        async with self.session.post(f"https://login.{BASE_URL.split('//')[1]}", data=auth_data) as response:
            if response.status == 200:
                # TODO: Add check for current user
                body = await response.text()
                info = ujson.loads(body.split('<script type="text/javascript">')[1].split(';</script>')[0][13:].strip())
                self.user = EUserSchema(**info["user"])

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
