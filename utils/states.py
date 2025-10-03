from aiogram.fsm.state import State, StatesGroup


class SetLang(StatesGroup):
    select_lang = State()


class Registration(StatesGroup):
    login = State()
    password = State()
