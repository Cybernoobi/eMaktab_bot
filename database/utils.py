from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from utils.enums import LocalizationLiteral
from .models import TelegramUser, eMaktabUser, async_session


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
            await session.commit()


async def add_em_user(user_id: int, login: str, password: str, **kwargs) -> None:
    async with async_session() as session:
        user = await session.scalar(select(TelegramUser).where(eMaktabUser.telegram_id == user_id))

        if not user:
            session.add(eMaktabUser(telegram_id=user_id,
                                    login=login,
                                    password=password))
            await session.commit()


async def get_user_for_tg_id(user_id: int, filter: Literal['tg', 'em']) -> TelegramUser | eMaktabUser | None:
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


async def get_all_users(filter: Literal['tg', 'em']) -> list[TelegramUser] | list[eMaktabUser]:
    if filter == "tg":
        async with async_session() as session:
            return await session.scalars(select(TelegramUser)).all()

    elif filter == "em":
        async with async_session() as session:
            return await session.scalars(select(eMaktabUser)).all()

    else:
        raise ValueError("Invalid filter")
