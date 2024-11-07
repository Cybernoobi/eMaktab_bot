# Base
from aiogram import F, Router, types
from aiogram.filters import CommandStart, Command

# FSM
from aiogram.fsm.context import FSMContext
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.state import StatesGroup, State

# Local
# import utils.keyboard as kb
import utils_v2.states as st
import utils_v2.keyboard_v2 as kb
import utils_v2.site_utils_v2 as su
from utils.database import requests as rq
from utils.other_utils import MyFilter as MF
from utils.other_utils import load_message, validate_username, Langs

# Misc
from pprint import pprint

router = Router()


# Start command
@router.message(CommandStart())
async def start_command(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name

    __keyRemove = await message.answer('не читай', reply_markup=types.ReplyKeyboardRemove())
    await __keyRemove.delete()

    if await rq.check_user(user_id, fileter=MF.TELEGRAM):
        if await rq.check_user(user_id, fileter=MF.EMAKTAB):
            user_settings = await rq.get_user_settings(user_id)
            await message.answer(load_message("menu", user_settings.language),
                                 reply_markup=await kb.main(user_settings.language))

        else:
            if rq.check_privacy_policy(user_id) is False:
                text = f'[🇷🇺] {load_message("set_lang", Langs.RU)}\n[🇺🇿] {load_message("set_lang", Langs.UZ)}'
                await state.set_state(st.FirstStart.select_lang)
                await message.answer(text, reply_markup=await kb.set_lang(), parse_mode=ParseMode.HTML)
            else:
                pass

    else:
        await rq.add_tg_user(user_id, full_name, username)
        text = f'[🇷🇺] {load_message("set_lang", Langs.RU)}\n[🇺🇿] {load_message("set_lang", Langs.UZ)}'
        await state.set_state(st.FirstStart.select_lang)
        await message.answer(text, reply_markup=await kb.set_lang(), parse_mode=ParseMode.HTML)


@router.callback_query(st.FirstStart.select_lang, F.data.startswith('set_lang'))
async def set_lang(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = callback.data.split('set_lang_')[-1]

    await rq.set_lang(user_id, lang, True)
    await state.set_state(st.FirstStart.privacy_policy)
    await callback.message.answer(load_message("welcome", lang),
                                  reply_markup=await kb.privacy_policy(lang),
                                  parse_mode=ParseMode.HTML)


@router.callback_query(F.data.startswith('set_lang'))
async def edit_lang(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = callback.data.split('set_lang_')[-1]

    await callback.message.delete()

    if await rq.check_user(user_id, fileter=MF.EMAKTAB):
        await rq.set_lang(user_id, lang, False)
        await callback.message.answer(load_message("lang_switched", lang), parse_mode=ParseMode.HTML)


@router.callback_query(st.FirstStart.privacy_policy, F.data.startswith('privacy_policy_'))
async def privacy_policy(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()

    UserSettings = await rq.get_user_settings(callback.from_user.id)
    lang = UserSettings.language

    if callback.data == 'privacy_policy_success':
        await rq.privacy_policy_true(UserSettings.user_id)
        await callback.message.answer(load_message('login', lang), reply_markup=await kb.login(lang))

    elif callback.data == 'privacy_policy_fail':
        await callback.message.answer(load_message('privacy_policy_fail', lang), parse_mode=ParseMode.HTML)
        await rq.CASCADE_USER(UserSettings.user_id)

    await state.clear()


@router.callback_query(F.data == 'login')
async def login(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()

    UserSettings = await rq.get_user_settings(callback.from_user.id)
    await callback.message.answer(load_message('get_login', UserSettings.language))

    await state.update_data()


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
    await state.set_state(st.ForLogin.wait_login)
    await message.reply(load_message("get_login", UserSettings.language))


@router.message(st.ForLogin.wait_login)
async def process_login(message: types.Message, state: FSMContext):
    lang = await state.get_data()['lang']

    await state.update_data(login=message.text)
    await state.set_state(st.ForLogin.wait_password)
    await message.reply(load_message("get_password", lang))


@router.message(st.ForLogin.wait_password)
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
@router.message(Command('mark'))
async def marks(message: types.Message):
    await message.answer('⚡')
    user_id = message.from_user.id

    if rq.check_user(user_id, fileter=MF.EMAKTAB):
        data = await rq.get_emaktab(user_id)
        user = su.EmaktabManager(user_id, data.login, data.password)
        await user.init()
        await user.get_marks()
    else:
        if not rq.check_user(user_id, fileter=MF.USER_SETTINGS):
            text = (
                    load_message("click_btn_pls", Langs.RU)
                    + '\n' +
                    load_message("click_btn_pls", Langs.UZ)
            )
            await message.answer(text)
        else:
            uSettings = await rq.get_user_settings(user_id)
            await message.answer(load_message("click_btn_pls", uSettings.language))


# @router.message(Command('test'))
# async def test(message: types.Message):
#     await rq.privacy_policy(message.from_user.id)
#     await message.answer('Тестовая кнопка', reply_markup=await kb.test())


# Handled errors for FSM
@router.message(st.FirstStart.select_lang)
async def wait_end(message: types.Message):
    text = (
            load_message("click_btn_pls", Langs.RU)
            + '\n' +
            load_message("click_btn_pls", Langs.UZ)
    )
    await message.answer(text)


@router.message(st.FirstStart.privacy_policy)
async def wait_end(message: types.Message):
    text = (
            load_message("click_btn_pls", Langs.RU)
            + '\n' +
            load_message("click_btn_pls", Langs.UZ)
    )
    await message.answer(text)
