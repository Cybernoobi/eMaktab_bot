from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, BigInteger, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from config_reader import get_config, DBConfig

DATABASE_URL: DBConfig = get_config(model=DBConfig, root_key="database")

engine = create_async_engine(DATABASE_URL.uri.get_secret_value(), echo=True)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class TelegramUser(Base):
    __tablename__ = "telegram_users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    localization: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                 default=lambda: datetime.now(timezone.utc))

    emaktab_users: Mapped[list["eMaktabUser"]] = relationship("eMaktabUser", back_populates="telegram_user")


class eMaktabUser(Base):
    __tablename__ = "emaktab_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    login: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    telegram_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(TelegramUser.telegram_id, ondelete="CASCADE"),
                                             nullable=False)
    # localization: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                                 default=lambda: datetime.now(timezone.utc))

    # Отношение к TelegramUser, по которому будем получать localization
    telegram_user: Mapped["TelegramUser"] = relationship("TelegramUser", back_populates="emaktab_users",
                                                         primaryjoin="eMaktabUser.telegram_id == TelegramUser.telegram_id")

    @property
    def localization(self) -> str:
        """Получает localization напрямую из связанного TelegramUser."""
        return self.telegram_user.localization


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
