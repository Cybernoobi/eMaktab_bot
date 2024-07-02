# Base
from aiogram import F, Router, types
from aiogram.filters import CommandStart, Command

# Buttons
from aiogram.utils.keyboard import InlineKeyboardBuilder

# FSM
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

# Local
import utils.keyboard as kb
from utils.database import *
from utils.site_utils import emaktab_connect, emaktab_get_mark, emaktab_get_average_score
from utils.config import DATABASE_NAME

router = Router()


class LoginStates(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()




# Start command
@router.message(CommandStart())
async def start_command(message: types.Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username

    await message.answer(
        text=f'Добро пожаловать {full_name}.\nЭтот бот ещё в разработке, если есть вопросы пишите мне в лс @Cybernoobi')

    if not await check_user_tg(DATABASE_NAME, user_id):
        await add_tg_user(DATABASE_NAME, user_id, username, full_name)


# Delete telegram user command
@router.message(Command('delete'))
async def del_user(message: types.Message):
    await delete_tg_user(DATABASE_NAME, message.from_user.id)
    print(f'Пользователь {message.from_user.full_name} удалён')


# Login eMaktab user
@router.message(Command('login'))
async def start_login(message: types.Message, state: FSMContext):
    await state.set_state(LoginStates.waiting_for_login)
    await message.reply("Введите свой логин")


@router.message(LoginStates.waiting_for_login)
async def process_login(message: types.Message, state: FSMContext):
    await state.update_data(login=message.text)
    await state.set_state(LoginStates.waiting_for_password)
    await message.reply("Теперь введите свой пароль")


@router.message(LoginStates.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)

    data = await state.get_data()
    user_id = message.from_user.id
    login = data['login']
    password = data['password']

    result = await check_user_emaktab(DATABASE_NAME, login)

    if not result:
        text = await emaktab_connect(DATABASE_NAME, user_id, login, password)
        await message.answer(text=text)
    else:
        await message.answer(text='''
[RU] Эта учетная запись уже связана если вам нужна помощь, напишите в службу технической поддержки (они есть в описании)
[UZ] Ushbu hisob allaqachon bog'langan agar sizga yordam kerak bo'lsa, texnik yordamni yozing (ular tavsifda)''')

    await state.clear()  # clearing the state


# Logout eMaktab user
@router.message(Command('logout'))
async def logout_command(message: types.Message):
    await delete_emaktab_login(DATABASE_NAME, message.from_user.id)
    await message.answer(text='Вы удалены из базы')


# Get and print marks for eMaktab
@router.message(Command('mark'))
async def mark_command(message: types.Message):
    sent_message = await message.answer(text='⚡️')
    result = await get_user_to_user_id(DATABASE_NAME, message.from_user.id)

    if result is not None:
        login = result[1]
        password = result[2]

        item = await emaktab_get_mark(login, password)
        if item == 'Incorrect password':
            await sent_message.delete()
            await message.answer(
                text='Неправильный логин или пароль, для повторной регистрации введиьте /logout а потом /login')
        else:
            await sent_message.delete()
            await message.answer(text=item)
            # pprint(item)
    else:
        await sent_message.delete()
        await message.answer(text='Вы не зарегистрированы (/login)')


# Get and print average marks
@router.message(Command('average_score'))
async def average_score(message: types.Message):
    await message.reply("Выберите четверть:", reply_markup=await kb.average_score_buttons())


@router.callback_query()
async def process_callback(callback_query: types.CallbackQuery):
    sent_message = await callback_query.message.answer('⚡️')
    result = await get_user_to_user_id(DATABASE_NAME, callback_query.from_user.id)

    if result is not None:
        login = result[1]
        password = result[2]

        item = await emaktab_get_average_score(login, password, int(callback_query.data))
        if item == 'Incorrect password':
            await sent_message.delete()
            await callback_query.message.answer(
                                   'Неправильный логин или пароль, для повторной регистрации введиьте /logout а потом /login')
        elif item == 'Error 404':
            await sent_message.delete()
            await callback_query.message.answer('Сайт временно не отвечает')
        else:
            await sent_message.delete()
            await callback_query.message.answer(text=item)
            # pprint(item)
    else:
        await sent_message.delete()
        await callback_query.message.answer(text='Вы не зарегистрированы (/login)')
