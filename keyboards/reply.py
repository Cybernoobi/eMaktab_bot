from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup
from fluent.runtime import FluentLocalization


def main(l10n: FluentLocalization) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    for text in l10n.format_value(f"main-btn").split("\n"):
        kb.button(text=text)
    return kb.adjust(1, 2).as_markup(resize_keyboard=True)
