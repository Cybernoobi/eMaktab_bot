from aiogram import BaseMiddleware, Bot
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import Message


class ChattingStatusMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        bot: Bot = data["bot"]

        await bot.send_chat_action(
            chat_id=event.from_user.id,
            action="typing"
        )

        return await handler(event, data)
