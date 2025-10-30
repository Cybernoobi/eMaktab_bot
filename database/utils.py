from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from utils.enums import LocalizationLiteral
from .models import TelegramUser, eMaktabUser, async_session, UserSettings

Filter = Literal['tg', 'em']


async def add_tg_user(user_id: int, username: str | None, full_name: str, localization: LocalizationLiteral) -> None:
    """
    Adds a new user to the database if they do not already exist.

    :param user_id: The unique identifier for the user in Telegram.
    :param username: The username of the user in Telegram.
    :param full_name: The full name of the user in Telegram.
    :param localization: The localization of the user in Telegram.

    :return: None
    """
    async with async_session() as session:
        user = await session.scalar(select(TelegramUser).where(TelegramUser.telegram_id == user_id))

        if not user:
            session.add(TelegramUser(telegram_id=user_id,
                                     username=username,
                                     full_name=full_name,
                                     localization=localization))
            session.add(UserSettings(
                telegram_id=user_id
            ))
            await session.commit()


async def add_em_user(user_id: int, login: str, password: str, **kwargs) -> None:
    async with async_session() as session:
        user = await session.scalar(select(TelegramUser).where(eMaktabUser.telegram_id == user_id))

        if not user:
            session.add(eMaktabUser(telegram_id=user_id,
                                    login=login,
                                    password=password))
            await session.commit()


async def get_user_for_tg_id(user_id: int, filter: Filter) -> TelegramUser | eMaktabUser | None:
    async with async_session() as session:
        user = None
        if filter == 'tg':
            user = await session.scalar(select(TelegramUser).where(TelegramUser.telegram_id == user_id))

        elif filter == 'em':
            user = await session.scalar(
                select(eMaktabUser)
                .options(selectinload(eMaktabUser.telegram_user))
                .where(eMaktabUser.telegram_id == user_id)
            )

        return user


async def get_all_users(filter: Filter, only_id: bool = False) -> list[TelegramUser] | list[eMaktabUser]:
    stmt = {
        "tg": select(TelegramUser.telegram_id) if only_id else select(TelegramUser),
        "em": select(eMaktabUser.telegram_id) if only_id else select(eMaktabUser)
    }.get(filter, None)

    if stmt is None:
        raise ValueError("Invalid filter")

    async with async_session() as session:
        result = await session.scalars(stmt)
        return result.all()
