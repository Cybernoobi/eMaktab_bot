# Base
from aiogram import F, Router, types
from aiogram.filters import CommandStart, Command

# FSM
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.state import StatesGroup, State

# Local
# import utils.keyboard as kb
import utils_v2.site_utils_v2 as su
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
    username = message.from_user.username
    full_name = message.from_user.full_name

    if await rq.check_user(user_id, fileter='tg'):
        if rq.check_user(user_id, fileter='em'):
            await message.answer('Меню перезагружена', reply_markup=await kb.main(lang))
    else:
        await rq.add_tg_user(user_id, full_name, username)
        text = f'[🇷🇺] {load_message("set_lang", "ru-RU")}\n[🇺🇿] {load_message("set_lang", "uz-Latn-UZ")}'
        await message.answer(text, reply_markup=await kb.set_lang(), parse_mode=ParseMode.HTML)


@router.callback_query(F.data.startswith('set_lang'))
async def set_lang(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = callback.data.split('set_lang_')[-1]

    await callback.message.delete()

    if await rq.check_user(user_id, fileter='em'):
        await rq.set_lang(user_id, lang, False)
        await callback.message.answer(load_message("lang_switched", lang), parse_mode=ParseMode.HTML)

    else:
        await rq.set_lang(user_id, lang, True)
        await callback.message.answer(load_message("welcome", lang),
                                      reply_markup=await kb.privacy_policy(lang),
                                      parse_mode=ParseMode.HTML)


@router.callback_query(F.data.startswith('privacy_policy_'))
async def privacy_policy(callback: types.CallbackQuery):
    await callback.message.delete()

    UserSettings = await rq.get_user_settings(callback.from_user.id)
    lang = UserSettings.language

    if callback.data == 'privacy_policy_success':
        await rq.privacy_policy_true(UserSettings.user_id)
        await callback.message.answer(load_message('login', lang), reply_markup=await kb.login(lang))

    elif callback.data == 'privacy_policy_fail':
        await callback.message.answer(load_message('privacy_policy_fail.json', lang), parse_mode=ParseMode.HTML)
        await rq.CASCADE_USER(UserSettings.user_id)


# Delete telegram user command
# @router.message(Command('delete'))
# async def del_user(message: types.Message):
#     await delete_tg_user(DATABASE_NAME, message.from_user.id)
#     print(f'Пользователь {message.from_user.full_name} удалён')


# Login eMaktab user
@router.message(Command('login'))
async def start_login(message: types.Message, state: FSMContext):
    UserSettings = await rq.get_user_settings(message.from_user.id)

    await state.update_data(lang=UserSettings.language)
    await state.set_state(LoginStates.wait_login)
    await message.reply(load_message("get_login", UserSettings.language))


@router.message(LoginStates.wait_login)
async def process_login(message: types.Message, state: FSMContext):
    lang = await state.get_data()['lang']

    await state.update_data(login=message.text)
    await state.set_state(LoginStates.wait_password)
    await message.reply(load_message("get_password", lang))


@router.message(LoginStates.wait_password)
async def process_password(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)

    data = await state.get_data()

    user_id = message.from_user.id
    login = data['login']
    password = data['password']
    lang = data['lang']

    if not await rq.get_emaktab(user_id, login, password):
        EM = su.EmaktabManager(user_id, login, password)
        await EM.init()
        result = await EM.first_login()

        if result:
            await message.answer(load_message("login_success", lang), parse_mode=ParseMode.HTML)
    else:
        await message.answer(load_message("error_connected_account", lang))

    await state.clear()  # clearing the state


@router.message(F.text == 'Недавние оценки')
@router.message(Command('marks'))
async def marks(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    User = rq.get_user_settings(user_id)


@router.message(Command('test'))
async def test(message: types.Message):
    await rq.privacy_policy(message.from_user.id)
    # await message.answer('Тестовая кнопка', reply_markup=await kb.test())
