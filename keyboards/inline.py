from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton
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


def create_calendar(func_name: str, year: int, month: int, l10n: FluentLocalization):
    import calendar
    kb = InlineKeyboardBuilder()

    # Название месяца и стрелки
    prev_month = month - 1 if month > 1 else 12
    next_month = month + 1 if month < 12 else 1
    prev_year = year if month > 1 else year - 1
    next_year = year if month < 12 else year + 1

    kb.row(
        InlineKeyboardButton(text="←", callback_data=f"{func_name}:calendar:{prev_year}:{prev_month}"),
        InlineKeyboardButton(text=f"{calendar.month_name[month]} {year}", callback_data="ignore"),
        InlineKeyboardButton(text="→", callback_data=f"{func_name}:calendar:{next_year}:{next_month}")
    )

    # Дни недели
    days_of_week = l10n.format_value("days-of-week").strip().split(", ")
    for day in days_of_week:
        kb.button(text=day, callback_data="ignore")

    # Дни месяца
    month_days = calendar.monthcalendar(year, month)
    for week in month_days:
        for day in week:
            if day == 0:
                kb.button(text=" ", callback_data="ignore")
            else:
                kb.button(text=str(day), callback_data=f"{func_name}:day:{year}:{month}:{day}")

    return kb.adjust(3, 7).as_markup()
