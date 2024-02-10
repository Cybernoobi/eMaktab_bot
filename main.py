from aiogram import Dispatcher, Bot, executor
from aiogram.types import Message

# local
from database import check_user_tg, add_tg_user, delete_user
from config import TG_API, DATABASE_NAME
from loger import start_loging


async def on_startup(_):
    print('Бот успешно запушен')
    start_loging()


async def on_shutdown(_):
    print('Бот был остоновлен')


async def send_message(user_id: int, text: str):
    await bot.send_message(user_id, text)


bot = Bot(TG_API)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start_command(message: Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username

    await message.answer(
        text=f'Добро пожаловать {full_name}.\nЭтот бот ещё в разработке, если есть вопросы пишите мне в лс @Cybernoobi')

    if await check_user_tg(DATABASE_NAME, user_id):
        await message.answer(text='Вы уже зарегистрированны')
    else:
        await message.answer(text='Идёт авторизация')
        await add_tg_user(DATABASE_NAME, user_id, username, full_name)


@dp.message_handler(commands=['delete'])
async def create_db(message: Message):
    user_id = message.from_user.id
    await delete_user(DATABASE_NAME, user_id)


@dp.message_handler()
async def main(message: Message):
    if message.from_user.id == 5595813124:
        user_id = 900237952  # Замените на актуальный user_id
        await send_message(user_id, message.text)
        await message.answer(text='Сообщение отправлено')
    else:
        print(message.text)


if __name__ == '__main__':
    executor.start_polling(dp,
                           skip_updates=True,
                           on_startup=on_startup,
                           on_shutdown=on_shutdown)
