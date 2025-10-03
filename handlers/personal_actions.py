import structlog
from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, CallbackQuery, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder

from fluent.runtime import FluentLocalization

import keyboards.inline as kb_inline
import keyboards.reply as kb_reply
import utils.states as st
from EmaktabAPI import StudentClient
from EmaktabAPI.emaktab import localization_type
from EmaktabAPI.exceptions import InvalidLoginOrPassword, UnknownError
from utils.enums import Localization
import database.utils as db
from fluent_loader import L10N_MAPPING

# Declare router
router = Router()
router.message.filter(F.chat.type == "private")

# Declare logger
logger = structlog.get_logger()


# Declare handlers
@router.message(Command("start"))
async def cmd_owner_hello(message: Message, l10n: FluentLocalization, state: FSMContext):
    if await db.get_user_for_tg_id(message.from_user.id, 'tg'):
        if not await db.get_user_for_tg_id(message.from_user.id, 'em'):
            await state.set_state(st.Registration.login)
            await message.answer(l10n.format_value(f"enter-login-msg"), reply_markup=ReplyKeyboardRemove())
            return
        await message.answer(l10n.format_value(f"main-msg"), reply_markup=kb_reply.main(l10n))
        return

    await message.answer(l10n.format_value("hello-msg"), reply_markup=ReplyKeyboardRemove())
    await state.set_state(st.SetLang.select_lang)
    await message.answer(l10n.format_value("set-lang-msg").replace("\\", ""), reply_markup=kb_inline.set_lang(l10n))


@router.callback_query(st.SetLang.select_lang, F.data.startswith("set_lang_"))
async def set_lang(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    lang = {"ru": str(Localization.RU),
            "uz": str(Localization.UZ)}[callback.data.split("_")[-1]]
    l10n: FluentLocalization = L10N_MAPPING.get(lang)
    await db.add_tg_user(callback.from_user.id, callback.from_user.username, callback.from_user.full_name, lang)
    await state.set_state(st.Registration.login)
    await callback.message.answer(l10n.format_value(f"enter-login-msg"))


@router.message(st.Registration.login)
async def registration_login(message: Message, l10n: FluentLocalization, state: FSMContext):
    user = await db.get_user_for_tg_id(message.from_user.id, 'tg')
    await state.update_data(login=message.text)
    await state.update_data(localization=user.localization)
    await state.set_state(st.Registration.password)
    await message.answer(l10n.format_value(f"enter-password-msg"))


@router.message(st.Registration.password)
async def registration_password(message: Message, l10n: FluentLocalization, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    em_client = StudentClient(**data)

    try:
        await em_client.init()
        await db.add_em_user(message.from_user.id, **data)
        await message.answer(l10n.format_value(f"main-msg"), reply_markup=kb_reply.main(l10n))

    except InvalidLoginOrPassword:
        await message.answer(l10n.format_value(f"incorrect-login-or-password-msg"))
        await state.set_state(st.Registration.login)
        await message.answer(l10n.format_value(f"enter-login-msg"))

    except UnknownError as e:
        await message.answer(l10n.format_value(f"unknown-error-msg",
                                               {
                                                   "time": str(e.args[2]),
                                                   "exceptClass": str(e.args[1].__class__.__name__)
                                               }))
        await message.answer(l10n.format_value(f"re-registration-msg"))
        raise e.args[1]

    finally:
        await state.clear()


@router.message()
async def handle_message(message: Message, l10n: FluentLocalization):
    commands = l10n.format_value("main-btn").split("\n")
    if not message.text in commands:
        await message.answer(l10n.format_value("unknown-message"))
        return

    elif message.text.startswith("🎩") or message.text.startswith("📌") or message.text.startswith("⚙️"):
        await message.answer(l10n.format_value("in-dev"))
        return

    try:
        em_db = await db.get_user_for_tg_id(message.from_user.id, 'em')
        tg_db = await db.get_user_for_tg_id(message.from_user.id, 'tg')

        em_client = await StudentClient(login=str(em_db.login), password=str(em_db.password), localization=tg_db.localization).init()
        if message.text.startswith("⌛"):
            marks = await em_client.get_marks()
            result = ""
            for mark in marks:
                result += f"{mark.subject.name}: {mark.marks[0].value}\n"
            await message.reply(result)

    except Exception as e:
        # await message.answer(l10n.format_value("unknown-error-msg",
        #                                        {
        #                                            "time": str(e.args[2] or "not set"),
        #                                            "exceptClass": str(e.args[1].__class__.__name__) or str(e.__class__.__name__)
        #                                        }))
        await message.answer(l10n.format_value("re-registration-msg"))
        raise e