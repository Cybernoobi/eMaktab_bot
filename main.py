from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Dispatcher, Bot, executor
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

# local
from utils.database import check_user_tg, add_tg_user, delete_user, check_user_emaktab
from utils.config import TG_API, DATABASE_NAME
from utils.site_utils import emaktab_connect


async def on_startup(_):
    print('The bot has started')


async def on_shutdown(_):
    print('The bot is stopped')


class LoginStates(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()


bot = Bot(TG_API)
dp = Dispatcher(bot, storage=MemoryStorage())


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
async def del_user(message: Message):
    user_id = message.from_user.id
    await delete_user(DATABASE_NAME, user_id)


@dp.message_handler(commands=['login'])
async def start_login(message: Message, state: FSMContext):
    await message.reply("Введите свой логин")
    await LoginStates.waiting_for_login.set()


@dp.message_handler(state=LoginStates.waiting_for_login)
async def process_login(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['login'] = message.text
    await message.reply("Теперь введите свой пароль")
    await LoginStates.waiting_for_password.set()


@dp.message_handler(state=LoginStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    async with state.proxy() as data:
        user_id = message.from_user.id
        login = data['login']
        password = message.text

        result = await check_user_emaktab(DATABASE_NAME, login)

        if not result:
            print('регистрация')
            text = await emaktab_connect(DATABASE_NAME, user_id, login, password)
            await message.answer(text=text)
        else:
            await message.answer(text='''
[RU] Эта учетная запись уже связана если вам нужна помощь, напишите в службу технической поддержки (они есть в описании)
[UZ] Ushbu hisob allaqachon bog'langan agar sizga yordam kerak bo'lsa, texnik yordamni yozing (ular tavsifda)''')

    await state.finish()  # clearing the state


if __name__ == '__main__':
    executor.start_polling(dp,
                           skip_updates=True,
                           on_startup=on_startup,
                           on_shutdown=on_shutdown)
