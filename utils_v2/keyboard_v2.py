from aiogram.utils.keyboard import (InlineKeyboardBuilder, InlineKeyboardMarkup,
                                    ReplyKeyboardBuilder, ReplyKeyboardMarkup)
from utils.other_utils import load_message


async def set_lang():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="[🇷🇺] Русский язык", callback_data="set_lang_ru-RU")
    keyboard.button(text="[🇺🇿] O'zbek tili", callback_data="set_lang_uz-Latn-UZ")

    return keyboard.adjust(1).as_markup()


async def start(lang: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text=f"{load_message('login_btn', lang)} ⚡", callback_data="login")

    return keyboard.as_markup()


async def main() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()

    keyboard.button(text="Профиль 🎩 (В разработке)")
    keyboard.button(text="Расписание 🕰️ (В разработке)")
    keyboard.button(text="Настройки ⚙️ (В разработке)")
    keyboard.button(text="Оценки ⚡ (Бета)")

    return keyboard.adjust(2).as_markup()


async def average_score_buttons():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="1-ая четверть", callback_data='1')
    keyboard.button(text="2-ая четверть", callback_data='2')
    keyboard.button(text="3-ая четверть", callback_data='3')
    keyboard.button(text="4-ая четверть", callback_data='4')
    keyboard.button(text="Итоги", callback_data='5')

    return keyboard.adjust(2).as_markup()
