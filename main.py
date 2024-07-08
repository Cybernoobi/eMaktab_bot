from aiogram import Bot, Dispatcher
from aiogram.methods import DeleteWebhook
from aiogram.fsm.storage.memory import MemoryStorage


# local
from utils.database.models import async_main
from utils.database import requests as rq
from utils.config import TG_API
from utils.hendlers import router


async def on_startup(dispatcher: Dispatcher):
    print('The bot has started')


async def on_shutdown(dispatcher: Dispatcher):
    print('The bot is stopped')


async def main():
    await async_main()
    bot = Bot(TG_API)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


if __name__ == '__main__':
    import asyncio
    import logging

    try:
        logging.basicConfig(level=logging.INFO)
        asyncio.run(main())
    except KeyboardInterrupt:
        print('exit')
