from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from utils.config import DATABASE_NAME

engine = create_async_engine(url=f'sqlite+aiosqlite:///{DATABASE_NAME}')

async_session = async_sessionmaker(engine)


class CyberDataBase(AsyncAttrs, DeclarativeBase):
    pass


class UserTelegram(CyberDataBase):
    __tablename__ = 'tg_users'

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, unique=True)
    username: Mapped[str] = mapped_column(String(35))
    full_name: Mapped[str] = mapped_column(String(130))
    registration_date: Mapped[str] = mapped_column(String(130))


class EmaktabUsers(CyberDataBase):
    __tablename__ = 'emaktab'

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('tg_users.user_id'), primary_key=True)
    login: Mapped[str] = mapped_column(String(25))
    password: Mapped[str] = mapped_column(String(50))


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(CyberDataBase.metadata.create_all)
