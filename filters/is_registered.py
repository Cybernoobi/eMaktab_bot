from aiogram.filters import BaseFilter
from aiogram.types import Message

from database.utils import get_all_users

class IsRegisteredFilter(BaseFilter):
    def __init__(self, is_registered):
        self.is_owner = is_registered

    async def __call__(self, message: Message) -> bool:
        users = [em_data.telegram_id for em_data in await get_all_users("em")]
        return message.from_user.id in users
