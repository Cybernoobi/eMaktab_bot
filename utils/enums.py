from enum import StrEnum
from typing import Literal


class Localization(StrEnum):
    RU = "ru-RU"
    UZ = "uz-Latn-UZ"


LocalizationLiteral = Literal["ru-RU", "uz-Latn-UZ"]
