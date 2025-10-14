from datetime import datetime, timezone, timedelta

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
from EmaktabAPI.schemas import UserStartPageInitialState
from utils import mood_to_emoji
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

@router.message(Command("password"))
async def get_password(message: Message):
    user = await db.get_user_for_tg_id(message.from_user.id, 'em')
    await message.reply(f"<tg-spoiler>{user.password}</tg-spoiler>")

@router.message(Command("logout"))
async def logout(message: Message):
    pass

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
        await message.answer(l10n.format_value(f"re-registration-msg"))
        # await state.set_state(st.Registration.login)
        # await message.answer(l10n.format_value(f"enter-login-msg"))

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


@router.message(Command("test"))
async def test(message: Message):
    await message.answer("test")


@router.message()
async def handle_message(message: Message, l10n: FluentLocalization, state: FSMContext):
    commands = l10n.format_value("main-btn").split("\n")
    if not message.text in commands:
        await message.answer(l10n.format_value("unknown-message"))
        return

    elif message.text.startswith("⚙️"):
        await message.answer(l10n.format_value("in-dev"))
        return

    try:
        em_db = await db.get_user_for_tg_id(message.from_user.id, 'em')
        em_client = await StudentClient(login=str(em_db.login), password=str(em_db.password),
                                        localization=em_db.localization).init()

        if message.text.startswith("📌"):
            try:
                # em_db = await db.get_user_for_tg_id(message.from_user.id, 'em')
                # em_client = StudentClient(login=str(em_db.login), password=str(em_db.password),
                #                           localization=em_db.localization)
                await em_client.init()
                if schedule := await em_client.get_schedule():
                    # await message.answer()
                    result = ""
                    for day in schedule:
                        result += f"\n📌 {day.date.strftime('%d.%m.%Y')}:\n"

                        for lesson in sorted(day.lessons, key=lambda x: x.number):
                            result += f"{lesson.number}. {lesson.subject.name}\n"
                    # await callback.message.answer(result)
                    await message.answer(result)
            except UnknownError as e:
                await message.answer(l10n.format_value("unknown-error-msg",
                                                       {
                                                           "time": str(e.args[2] or "not set"),
                                                           "exceptClass": str(
                                                               e.args[1].__class__.__name__) or str(
                                                               e.__class__.__name__)
                                                       }))
                raise e


        elif message.text.startswith("🎩"):
            context = await em_client.get_profile()
            await message.reply_photo(context.avatar_url,
                                      caption=l10n.format_value("profile-msg", {
                                          "full_name": f"{context.last_name} {context.first_name} {context.middle_name}",
                                          "school": context.school.name,
                                          "edu_class": context.group_name,
                                          "age": str(context.user_age),
                                          "teacher": context.class_teacher_name,
                                      }))

        elif message.text.startswith("⌛"):
            await message.answer(l10n.format_value("marks-msg"), reply_markup=kb_inline.get_marks(l10n))

    except InvalidLoginOrPassword:
        await message.answer(l10n.format_value("incorrect-login-or-password-msg"))
        await message.answer(l10n.format_value("re-registration-msg"))
        # await state.set_state(st.Registration.login)
        # await message.answer(l10n.format_value("enter-login-msg"))

    except UnknownError as e:
        await message.answer(l10n.format_value("unknown-error-msg",
                                               {
                                                   "time": str(e.args[2] or "not set"),
                                                   "exceptClass": str(e.args[1].__class__.__name__)
                                               }))
        raise e.args[1]


@router.callback_query(F.data == "get_recent_marks")
async def get_recent_marks(callback: CallbackQuery, l10n: FluentLocalization):
    em_db = await db.get_user_for_tg_id(callback.from_user.id, 'em')
    em_client = StudentClient(login=str(em_db.login), password=str(em_db.password),
                              localization=em_db.localization)
    await em_client.init()
    dates: dict[str, list[UserStartPageInitialState.UserMarks.Child.Mark]] = {}
    result = ""
    for mark in await em_client.get_recent_marks():
        date = mark.date.astimezone(timezone(timedelta(hours=5), "Tashkent")).strftime("%d.%m.%Y")
        if not dates.get(date):
            dates[date] = []
        dates[date].append(mark)

    for time, marks in dates.items():
        text = l10n.format_value("marks-text", {"time": time}) + "\n<blockquote>"
        for m in marks:
            max_value = "/" + m.marks[0].max_value if m.marks[0].max_value else ""
            text += f"{mood_to_emoji(m.marks[0].mood.lower())}{m.subject.name}: {m.marks[0].value}{max_value} ({m.short_mark_type_text})\n"

        result += text + "</blockquote>\n"
    # print(dates)
    await callback.answer()
    await callback.message.answer(result)


@router.callback_query(F.data == "get_marks")
async def get_marks(callback: CallbackQuery, l10n: FluentLocalization):
    await callback.answer()
    await callback.message.answer(l10n.format_value("in-dev"))
    # try:
    #     em_db = await db.get_user_for_tg_id(callback.from_user.id, 'em')
    #     em_client = StudentClient(login=str(em_db.login), password=str(em_db.password),
    #                                     localization=em_db.localization)
    #     if schedule := await em_client.get_schedule():
    #         await callback.answer()
    #         result = ""
    #         for day in schedule:
    #             result += f"\n📌 {day.date.strftime('%d.%m.%Y')}:\n"
    #
    #             for lesson in sorted(day.lessons, key=lambda x: x.number):
    #                 result += f"{lesson.number}. {lesson.subject.name}\n"
    #         await callback.message.answer(result)
    # except UnknownError as e:
    #     await callback.answer(l10n.format_value("unknown-error-msg",
    #                                             {
    #                                                 "time": str(e.args[2] or "not set"),
    #                                                 "exceptClass": str(e.args[1].__class__.__name__) or str(e.__class__.__name__)
    #                                             }))
    #     await callback.message.answer(l10n.format_value("re-registration-msg"))
    #     raise e
