from aiogram.fsm.state import StatesGroup, State


class FirstStart(StatesGroup):
    select_lang = State()
    privacy_policy = State()


class ForLogin(StatesGroup):
    wait_login = State()
    wait_password = State()


class ForSelect(StatesGroup):
    language = State()


