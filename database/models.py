import datetime
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, BigInteger, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from config_reader import get_config, DBConfig

DATABASE_URL: DBConfig = get_config(model=DBConfig, root_key="database_url")

engine = create_async_engine(DATABASE_URL.uri.get_secret_value(), echo=True)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass


class TelegramUser(Base):
    __tablename__ = "telegram_users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    telegram_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, default=datetime.timezone.utc)


class eMaktabUser(Base):
    __tablename__ = "emaktab_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(TelegramUser.telegram_id), nullable=False)
    auth_token: Mapped[str] = mapped_column(String(350), nullable=False)
    person_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    school_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)