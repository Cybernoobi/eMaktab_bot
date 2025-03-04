from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import (InlineKeyboardBuilder, InlineKeyboardMarkup,
                                    ReplyKeyboardBuilder, ReplyKeyboardMarkup)
from utils.other_utils import load_message


async def main(lang: str) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()

    for text in load_message('menu_btns', lang):
        keyboard.button(text=text)

        # keyboard.button(text="Профиль 🎩 (В разработке)")
        # keyboard.button(text="Настройки ⚙️ (В разработке)")
        # keyboard.button(text="Расписание 🕰️ (В разработке)")
        # keyboard.button(text="Оценки ⚡ (Бета)")

    return keyboard.adjust(2).as_markup()


async def set_lang():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="[🇷🇺] Русский язык", callback_data="set_lang_ru-RU")
    keyboard.button(text="[🇺🇿] O'zbek tili", callback_data="set_lang_uz-Latn-UZ")

    return keyboard.adjust(1).as_markup()


async def privacy_policy(lang: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text=load_message('privacy_policy_btn', lang)[0], callback_data="privacy_policy_success")
    keyboard.button(text=load_message('privacy_policy_btn', lang)[1], callback_data="privacy_policy_fail")

    return keyboard.adjust(1).as_markup()


async def start(lang: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text=f"{load_message('login_btn', lang)} ⚡", callback_data="login")

    return keyboard.as_markup()


async def average_score_buttons():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="1-ая четверть", callback_data='1')
    keyboard.button(text="2-ая четверть", callback_data='2')
    keyboard.button(text="3-ая четверть", callback_data='3')
    keyboard.button(text="4-ая четверть", callback_data='4')
    keyboard.button(text="Итоги", callback_data='5')

    return keyboard.adjust(2).as_markup()


async def login(lang: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text=load_message('login_btn', lang)+' ⚡', callback_data="start_login")

    return keyboard.as_markup()

async def test():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text='Тест', web_app=WebAppInfo(url='https://ea428600-5bc1-41a6-9baf-c9b3f340896a-00-258fdvv8uuo17.pike.replit.dev/'))

    return keyboard.as_markup()