from datetime import datetime
from typing import Literal

import ujson
import lxml.html as lxml
from aiohttp import ClientSession, ClientResponse, FormData

from . import exceptions as exc
from .exceptions import InvalidLoginOrPassword
from .schemas import EUserAllInitialStates, EUserSchema, UserStartPageInitialState
from .utils import check_url, search_cookie, extract_js_vars_to_json

BASE_URL: str = "emaktab.uz"
localization_type = Literal["ru-RU", "uz-Latn-UZ"] | str


class Client:
    def __init__(self, login: str, password: str, localization: localization_type):
        self.session: ClientSession | None = None
        self.localization = localization
        self.auth_token: str | None = None
        self.auth_l: str | None = None

        self.login = login
        self.password = password

        self.user_initial_states: EUserAllInitialStates | None = None
        self.user: EUserSchema | None = None

    async def init(self):
        self.session = ClientSession(cookies={"Dnevnik_localization": self.localization})

        if not self.login or not self.password:
            raise exc.InvalidLoginOrPassword("Invalid login or password")
        await self.auth()
        return self

    async def _make_request(self, method: Literal["get", "post"], url: str, base_url=BASE_URL,
                            params: dict | None = None, data: dict | FormData | None = None, *args,
                            **kwargs) -> ClientResponse | None:
        async with self.session as session:
            base_url = f"https://{base_url}"
            if method == "get":
                async with session.get((base_url + url), params=params, data=data, *args, **kwargs) as response:
                    return response
            elif method == "post":
                async with session.post((base_url + url), params=params, data=data, *args, **kwargs) as response:
                    return response

    async def auth(self):
        auth_data = FormData()
        auth_data.add_field("login", self.login)
        auth_data.add_field("password", self.password)

        # auth_data.add_field("Captcha.Input", 13830)
        # auth_data.add_field("Captcha.Id", "c8745a25-9d03-4fe5-9f0b-c300d910008b")
        #
        # auth_data.add_field("exceededAttempts", False)

        async with self.session:
            async with self.session.post(f"https://login.{BASE_URL}", data=auth_data) as response:
                if response.status != 200:
                    raise exc.BadStatusCode(response.status, response)

                soup: lxml.HtmlElement = lxml.fromstring(await response.text())

                if str(response.url) not in [f"https://{BASE_URL}/userfeed", f"https://{BASE_URL}/teacher"]:
                    msg = soup.xpath('//div[@class="message "]')[0].text.strip()
                    if msg in ["Неправильно указан пароль или логин. Попробуйте еще раз.", "Parol yoki login notoʻgʻri koʻrsatilgan. Qaytadan urinib koʻring."]:
                        raise InvalidLoginOrPassword("Invalid login or password")

                    time = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
                    with open(f"log/{time}.html", "wb") as f:
                        f.write(lxml.tostring(soup))
                    raise exc.NoAuth(f"For some reason, the authorization failed. Link: {response.url}. Log in /log/{time}.html")

                dnevnik = ujson.loads(soup.xpath('/html/head/script[4]')[0].text.strip()[13:-1])
                states_info: EUserAllInitialStates | None = None

                for element in soup.xpath('/html/body/script'):
                    if not element.text:
                        continue
                    if element.text.strip().startswith("window.__S"):
                        try:
                            json_data = extract_js_vars_to_json(element.text)
                            states_info = EUserAllInitialStates(**ujson.loads(json_data))
                        except Exception as e:
                            time = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
                            with open(f"log/{time}.html", "wb") as f:
                                f.write(lxml.tostring(soup))
                            raise exc.UnknownError("Unknown error", e, time)

                if not states_info:
                    time = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
                    with open(f"log/{time}.html", "wb") as f:
                        f.write(lxml.tostring(soup))
                    raise exc.NoAuth(f"For some reason, the authorization failed. Log in /log/{time}.html")

                if not dnevnik["auth"]["isAuthenticated"]:
                    raise exc.InvalidLoginOrPassword("Invalid login or password")

                self.auth_token = search_cookie(response, "UZDnevnikAuth_a")
                self.auth_l = search_cookie(response, "UZDnevnikAuth_l")
                self.user = EUserSchema(**dnevnik["user"])
                self.user_initial_states = states_info

                return True


class StudentClient(Client):
    def __init__(self, login: str, password: str, localization: localization_type):
        super().__init__(login, password, localization)

    async def get_marks(self) -> list[UserStartPageInitialState.UserMarks.Child.Mark] | None:
        for child in self.user_initial_states.user_start_page.user_marks.children:
            if self.user_initial_states.user_start_page.user_marks.current_child.person_id == child.person_id:
                return child.marks


class TeacherClient(Client):
    def __init__(self, login: str, password: str, localization: localization_type):
        super().__init__(login, password, localization)

    async def student_reset_password(self, student_id: int, school_id: int):
        if self.user.common_role != "staff":
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
