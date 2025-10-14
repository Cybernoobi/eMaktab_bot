from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import Message

from database.utils import get_user_for_tg_id  # функция, возвращающая данные пользователя (login, password, localization)
from EmaktabAPI import StudentClient  # твой класс клиента


class EmaktabMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id

        # Проверяем, зарегистрирован ли пользователь
        user = await get_user_for_tg_id(user_id, filter="em")
        if not user:
            # Просто продолжаем, если пользователь не найден
            return await handler(event, data)

        # Создаём клиент и инициализируем сессии
        em_client = StudentClient(
            login=str(user.login),
            password=str(user.password),
            localization=user.localization
        )
        await em_client.init()

        # Добавляем клиента в контекст данных
        data["em_client"] = em_client

        try:
            # Передаём управление хэндлеру
            return await handler(event, data)
        finally:
            # Закрываем сессию клиента после выполнения
            await em_client.close()
