from aiogram.utils.keyboard import (InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton,
                                    ReplyKeyboardBuilder, ReplyKeyboardMarkup)


async def start() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Зарегистрироваться ⚡", callback_data="login")

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
    keyboard.adjust(2)

    return keyboard.as_markup()
