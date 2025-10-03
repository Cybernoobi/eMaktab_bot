from enum import StrEnum
from typing import Literal


class Localization(StrEnum):
    RU = "ru-RU"
    UZ = "uz-Latn-UZ"

LocalizationLiteral = Literal["ru-RU", "uz-Latn-UZ"]

class MessageTextRu(StrEnum):
    PROFILE = "🎩 Профиль"
    RECENT_ESTIMATES = "⌛ Недавние оценки"
    SCHEDULE = "📌 Расписание (В разработке)"


class MessageTextUz(StrEnum):
    PROFILE = "🎩 Профиль"
    RECENT_ESTIMATES = "⌛ Недавние оценки"
    SCHEDULE = "📌 Расписание (В разработке)"