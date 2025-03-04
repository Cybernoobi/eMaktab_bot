from sqlalchemy import BigInteger, String, ForeignKey, Boolean
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
    username: Mapped[str] = mapped_column(String(35), nullable=True)
    full_name: Mapped[str] = mapped_column(String(130))
    registration_date: Mapped[str] = mapped_column(String(130))

    def __repr__(self):
        return f'<UserTelegram {self.full_name} id={self.user_id}>'


class EmaktabUsers(CyberDataBase):
    __tablename__ = 'emaktab'

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(UserTelegram.user_id), primary_key=True)
    login: Mapped[str] = mapped_column(String(25))
    password: Mapped[str] = mapped_column(String(50))

    def __repr__(self) -> str:
        return f'<EmaktabUser {self.login}>'


class UserSettings(CyberDataBase):
    __tablename__ = 'settings'

    user_id: Mapped[int] = mapped_column(ForeignKey(UserTelegram.user_id), primary_key=True)
    language: Mapped[str] = mapped_column(String(10))
    account_type: Mapped[str] = mapped_column(String(10), server_default='student', nullable=True)  # student, parent, teacher
    privacy_policy: Mapped[bool] = mapped_column(Boolean, server_default='0')


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(CyberDataBase.metadata.create_all)
