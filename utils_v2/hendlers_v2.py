# Base
from aiogram import F, Router, types
from aiogram.filters import CommandStart, Command

# FSM
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.state import StatesGroup, State

# Local
# import utils.keyboard as kb
import utils.site_utils as su
import utils_v2.keyboard_v2 as kb
from utils.database import requests as rq
from utils.other_utils import load_message

# Misc
from pprint import pprint

router = Router()


class LoginStates(StatesGroup):
    set_lang = State()
    wait_login = State()
    wait_password = State()


# Start command
@router.message(CommandStart())
async def start_command(message: types.Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username

    if await rq.check_telegram_user(user_id):
        # await rq.add_tg_user(user_id, full_name, username)
        pass
    else:
        text = f'[🇷🇺] {load_message("set_lang", "ru-RU")}\n[🇺🇿] {load_message("set_lang", "uz-Latn-UZ")}'
        await message.answer(text, reply_markup=await kb.set_lang(), parse_mode=ParseMode.HTML)


@router.callback_query(F.data.startswith('set_lang'))
async def set_lang(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = callback.data.split('set_lang_')[-1]
    print(lang)
    # await rq.set_lang(user_id, lang)

# Delete telegram user command
# @router.message(Command('delete'))
# async def del_user(message: types.Message):
#     await delete_tg_user(DATABASE_NAME, message.from_user.id)
#     print(f'Пользователь {message.from_user.full_name} удалён')


# Login eMaktab user
@router.message(Command('login'))
async def start_login(message: types.Message, state: FSMContext):
    await state.set_state(LoginStates.wait_login)
    await message.reply("Введите свой логин")


@router.message(LoginStates.wait_login)
async def process_login(message: types.Message, state: FSMContext):
    await state.update_data(login=message.text)
    await state.set_state(LoginStates.wait_password)
    await message.reply("Теперь введите свой пароль")


@router.message(LoginStates.wait_password)
async def process_password(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)

    data = await state.get_data()
    user_id = message.from_user.id
    login = data['login']
    password = data['password']

    if not await rq.get_emaktab(user_id, login, password):
        result = await su.emaktab_connect(user_id, login, password)

        await message.answer(text=result)
    else:
        await message.answer(text='''
[RU] Эта учетная запись уже связана если вам нужна помощь, напишите в службу технической поддержки (они есть в описании)
[UZ] Ushbu hisob allaqachon bog'langan agar sizga yordam kerak bo'lsa, texnik yordamni yozing (ular tavsifda)''')

    await state.clear()  # clearing the state


# Logout eMaktab user
@router.message(Command('logout'))
async def logout_command(message: types.Message):
    if await rq.get_emaktab(message.from_user.id, deleted=True) == 'success':
        await message.answer(text='Вы удалены из базы')
    else:
        await message.answer(text='Произошла ошибка')


# Get and print marks for eMaktab
@router.message(Command('mark'))
async def mark_command(message: types.Message):
    sent_message = await message.answer(text='⚡️')
    result = await rq.get_emaktab(message.from_user.id)

    if result.login is not None:
        login = result.login
        password = result.password

        item = await su.emaktab_get_mark(login, password)
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


# Get and print average score
@router.message(Command('average_score'))
async def average_score(message: types.Message):
    await message.reply("Выберите четверть:", reply_markup=await kb.average_score_buttons())


@router.callback_query()
async def process_callback(callback_query: types.CallbackQuery):
    sent_message = await callback_query.message.answer('⚡️')
    result = await rq.get_emaktab(callback_query.from_user.id)

    if result.login is not None:
        login = result.login
        password = result.password

        item = await su.emaktab_get_average_score(login, password, int(callback_query.data))
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
