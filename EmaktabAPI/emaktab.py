import ujson
from aiohttp import ClientSession, ClientResponse, FormData
from bs4 import BeautifulSoup

from . import exceptions as exc
from .schemas import EFullInfoSchema
from .utils import check_url, search_cookie, full_info_to_class

BASE_URL: str = "emaktab.uz"


class Client:
    def __init__(self, login: str, password: str):
        self.session = ClientSession()

        self.auth_token: str = ""
        self.auth_l: str = ""

        self.login = login
        self.password = password
        self.full_info: EFullInfoSchema | None = None

    async def auth(self):
        auth_data = FormData()
        auth_data.add_field("login", self.login)
        auth_data.add_field("password", self.password)

        async with self.session:
            async with self.session.post(f"https://login.{BASE_URL}", data=auth_data) as response:
                if response.status != 200:
                    raise exc.BadStatusCode(response.status)

                soup = BeautifulSoup(await response.text(), "html.parser")
                full_info = soup.find_all("script", src=False, type=False)[11].text.strip()
                dnevnik = ujson.loads(soup.find("script", type="text/javascript").text.strip()[13:-1])

                full_info_to_class(full_info)

                if not dnevnik["auth"]["isAuthenticated"]:
                    raise exc.InvalidLoginOrPassword("Invalid login or password")

                self.auth_token = search_cookie(response, "UZDnevnikAuth_a")
                self.auth_l = search_cookie(response, "UZDnevnikAuth_l")



class StudentClient(Client):
    def __init__(self, login: str, password: str):
        super().__init__(login, password)

    async def get_marks(self):
        async with self.session:
            async with self.session.get(self.full_info.user__start__page__initial__state.urls.marks_url) as response:
                return response


class TeacherClient(Client):
    def __init__(self, login: str, password: str):
        super().__init__(login, password)

    async def student_reset_password(self, student_id: int, school_id: int):
        if self.user.commonRole != "staff":
            raise exc.ClientNotInTeacher("Client is not in teacher role")

        if school_id not in self.user.schools:
            raise exc.TeacherPermissionDenied("Teacher does not have permission to reset password for this school")

        async with self.session:

            params = {
                "person": student_id,
                "school": school_id,
                "view": "password"
            }

            async with self.session.post(check_url(f"schools.{BASE_URL}/v2/admin/persons/person"),
                                         params=params) as response:
                return response.text()
