import ujson
from aiohttp import ClientSession, FormData

from . import exceptions as exc
from .schemas import EUserSchema
from .utils import check_url

BASE_URL: str = "emaktab.uz"


class Client:
    def __init__(self, login: str, password: str):
        self.session = ClientSession()

        self.auth_token: str = ""
        self.auth_l: str = ""

        self.login = login
        self.password = password
        self.user: EUserSchema | None = None

    async def auth(self):
        auth_data = FormData()
        auth_data.add_field("login", self.login)
        auth_data.add_field("password", self.password)

        async with self.session:
            async with self.session.post(f"https://login.{BASE_URL}", data=auth_data) as response:
                if response.status != 200:
                    raise exc.BadStatusCode(response.status)

                body = await response.text()
                info = ujson.loads(body.split('<script type="text/javascript">')[1].split(';</script>')[0][13:].strip())

                if not info["auth"]["isAuthenticated"]:
                    raise exc.InvalidLoginOrPassword("Invalid login or password")

                self.user = EUserSchema.model_validate(info["user"])

                self.auth_token = response.history[0].cookies.get("UZDnevnikAuth_a").value
                self.auth_l = response.history[0].cookies.get("UZDnevnikAuth_l").value

    async def get_me(self):
        pass




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
