from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup
from fluent.runtime import FluentLocalization


def set_lang(l10n: FluentLocalization) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for text in l10n.format_value("set-lang-btn").split("\n"):
        text = text.split(" | ")
        kb.button(text=text[0], callback_data=text[1])
    return kb.as_markup()

def get_marks(l10n: FluentLocalization) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for text in l10n.format_value("marks-btn").split("\n"):
        text = text.split(" | ")
        kb.button(text=text[0], callback_data=text[1])
    return kb.as_markup()