from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message
from fluent.runtime import FluentLocalization

import database.utils as db


# Inner-middleware for message
class L10nMiddleware(BaseMiddleware):

    # 1. Принимаем словарь всех локализаций при инициализации
    # (например, {'ru-RU': FluentLocalization_ru, 'uz-Latn-UZ': FluentLocalization_uz})
    def __init__(self, l10n_mapping: Dict[str, FluentLocalization]):
        self.l10n_mapping = l10n_mapping
        # Локаль по умолчанию, если пользователь не найден (например, при первом запуске)
        self.default_locale_code = "en-US"
        self.default_l10n = self.l10n_mapping.get(self.default_locale_code)

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:

        user_id = event.from_user.id

        # 2. Получаем данные пользователя из базы данных
        # Предполагаем, что db.get_user_for_tg_id возвращает объект с полем .localization
        user = await db.get_user_for_tg_id(user_id, 'tg')

        # 3. Определяем нужный код локали
        if user and user.localization in self.l10n_mapping:
            # Используем локаль, сохраненную в БД
            locale_code = user.localization
        else:
            # Используем локаль по умолчанию
            locale_code = self.default_locale_code

        # 4. Извлекаем нужный объект FluentLocalization из карты
        l10n = self.l10n_mapping.get(locale_code, self.default_l10n)

        # 5. Передаем объект l10n в обработчик
        data["l10n"] = l10n

        return await handler(event, data)