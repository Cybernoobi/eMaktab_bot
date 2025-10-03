from typing import Dict
from pathlib import Path
from fluent.runtime import FluentLocalization, FluentResourceLoader

# Определяем соответствие кода локали и имени файла
# 'ru-RU' и 'uz-Latn-UZ' — это полные коды локалей, которые вы храните в БД
# 'ru' и 'uz' — это префиксы файлов, которые вы используете (ru.ftl, uz.ftl)
LOCALE_MAP = {
    "ru-RU": "ru",
    "uz-Latn-UZ": "uz",
    "en-US": "locale"
}


def get_l10n_mapping() -> Dict[str, FluentLocalization]:
    """
    Загружает все файлы локалей (ru.ftl, uz.ftl) из папки 'l10n'
    и возвращает словарь {locale_code: FluentLocalization_object}.
    """

    # 1. Проверка пути и папки 'l10n'
    # __file__ может находиться в другой папке, поэтому лучше использовать Path(__file__).parent
    locale_dir = Path(__file__).parent.joinpath("l10n")
    if not locale_dir.exists() or not locale_dir.is_dir():
        error = f"'l10n' directory not found at {locale_dir.absolute()}"
        raise FileNotFoundError(error)

    # 2. Инициализация загрузчика ресурсов
    # Загрузчик должен указывать на КОРЕНЬ папки locales, а не на конкретный файл
    l10n_loader = FluentResourceLoader(str(locale_dir.absolute()))

    # 3. Загрузка всех локалей
    l10n_mapping = {}

    for locale_code, file_prefix in LOCALE_MAP.items():
        # Проверяем наличие файла (например, ru.ftl)
        locale_file = locale_dir.joinpath(f"{file_prefix}.ftl")
        if not locale_file.exists():
            error = f"Locale file '{file_prefix}.ftl' not found in 'l10n' directory."
            raise FileNotFoundError(error)

        # Создаем FluentLocalization для каждого языка
        l10n_mapping[locale_code] = FluentLocalization(
            # Коды локалей для Fluent (должны совпадать с ключами в LOCALE_MAP)
            locales=[locale_code],
            # Имена файлов (БЕЗ пути, так как используется l10n_loader)
            resource_ids=[f"{file_prefix}.ftl"],
            resource_loader=l10n_loader
        )

    return l10n_mapping


# Загружаем карту при импорте модуля
L10N_MAPPING = get_l10n_mapping()