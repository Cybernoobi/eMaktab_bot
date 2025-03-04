from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton


async def average_score_buttons():
    keyboard = InlineKeyboardBuilder()

    keyboard.button(text="1-ая четверть", callback_data='1')
    keyboard.button(text="2-ая четверть", callback_data='2')
    keyboard.button(text="3-ая четверть", callback_data='3')
    keyboard.button(text="4-ая четверть", callback_data='4')
    keyboard.button(text="Итоги", callback_data='5')

    return keyboard.adjust(2).as_markup()

