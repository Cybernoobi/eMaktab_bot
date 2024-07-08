from utils.database.models import async_session
from utils.database.models import UserTelegram, EmaktabUsers
from sqlalchemy import select
from datetime import datetime


async def add_tg_user(user_id: int, username: str, full_name: str) -> None:
    """
    Adds a new user to the database if they do not already exist.

    :param user_id: The unique identifier for the user in Telegram.
    :param username: The username of the user in Telegram.
    :param full_name: The full name of the user in Telegram.

    :return: None
    """
    async with async_session() as session:
        user = await session.scalar(select(UserTelegram).where(UserTelegram.user_id == user_id))

        if not user:
            reg_date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            session.add(UserTelegram(user_id=user_id,
                                     username=username,
                                     full_name=full_name,
                                     registration_date=reg_date))
            await session.commit()


async def get_emaktab(user_id: int, login: str = None, password: str = None, added=False, deleted=False):
    async with async_session() as session:
        e_user = await session.scalar(select(EmaktabUsers).where(EmaktabUsers.user_id == user_id))

        if e_user is None:
            if added is True:
                if login is None or password is None:
                    return 'error'
                else:
                    session.add(EmaktabUsers(user_id=user_id,
                                             login=login,
                                             password=password))
                    await session.commit()
                return 'success'

            return False

        elif deleted is True:
            await session.delete(e_user)
            await session.commit()

            return 'success'

        else:
            return e_user


async def delete_emaktab_login(user_id: int) -> None:
    async with async_session() as session:
        e_user = await session.scalar(select(EmaktabUsers).where(EmaktabUsers.user_id == user_id))

        if e_user:
            await session.delete(e_user)
            await session.commit()
# async def get_categories():
#     async with async_session() as session:
#         return await session.scalars(select(Category))
#
#
# async def get_category_item(category_id):
#     async with async_session() as session:
#         return await session.scalars(select(Item).where(Item.category == category_id))
#
#
# async def get_item(item_id):
#     async with async_session() as session:
#         return await session.scalar(select(Item).where(Item.id == item_id))
