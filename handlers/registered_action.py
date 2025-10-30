from datetime import datetime, timezone, timedelta

import structlog
from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    LabeledPrice,
    PreCheckoutQuery,
    CallbackQuery,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from fluent.runtime import FluentLocalization

from filters.is_registered import IsRegisteredFilter
import keyboards.inline as kb_inline
import keyboards.reply as kb_reply
import utils.states as st
from EmaktabAPI import StudentClient
from EmaktabAPI.emaktab import localization_type
from EmaktabAPI.exceptions import InvalidLoginOrPassword, UnknownError
from EmaktabAPI.schemas import UserStartPageInitialState, DairyDays
from middlewares import EmaktabMiddleware
from utils import mood_to_emoji
from utils.enums import Localization
import database.utils as db

# Declare router
router = Router()
router.message.filter(F.chat.type == "private", IsRegisteredFilter(is_registered=True))
router.message.middleware(EmaktabMiddleware())
# router.pre_checkout_query.outer_middleware(EmaktabMiddleware())
router.callback_query.middleware(EmaktabMiddleware())

# Declare logger
logger = structlog.get_logger()


@router.message(Command("me"))
async def get_me(message: Message, l10n: FluentLocalization, em_client: StudentClient):
    await message.reply(l10n.format_value("log-pass-msg", {"login": em_client.login, "password": em_client.password}))


@router.message(Command("logout"))
async def logout(message: Message, l10n: FluentLocalization):
    await message.answer(l10n.format_value("in-dev"))


@router.message(F.text.startswith("🎩"))
async def profile(message: Message, l10n: FluentLocalization, em_client: StudentClient):
    try:
        await em_client.init()
        context = await em_client.get_profile()
        await message.reply_photo(
            context.avatar_url,
            caption=l10n.format_value(
                "profile-msg",
                {
                    "full_name": f"{context.last_name} {context.first_name} {context.middle_name}",
                    "school": context.school.name,
                    "edu_class": context.group_name,
                    "age": str(context.user_age),
                    "teacher": context.class_teacher_name,
                },
            ),
        )
    except UnknownError as e:
        await message.answer(
            l10n.format_value(
                "unknown-error-msg",
                {
                    "time": str(e.args[2]),
                    "exceptClass": str(e.args[1].__class__.__name__)
                },
            )
        )

        raise e


@router.message(F.text.startswith("⌛"))
async def get_marks(message: Message, l10n: FluentLocalization):
    await message.answer(l10n.format_value("marks-msg"), reply_markup=kb_inline.get_marks(l10n))


@router.message(F.text.startswith("📌"))
async def get_schedule(message: Message, l10n: FluentLocalization, em_client: StudentClient):
    try:
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
        await message.answer(
            l10n.format_value(
                "unknown-error-msg",
                {
                    "time": str(e.args[2] or "not set"),
                    "exceptClass": str(e.args[1].__class__.__name__)
                                   or str(e.__class__.__name__),
                },
            )
        )
        raise e


@router.message(F.text.startswith("⚙️"))
async def settings(message: Message, l10n: FluentLocalization):
    await message.answer(l10n.format_value("in-dev"))


# @router.message()
# async def handle_message(message: Message, l10n: FluentLocalization, state: FSMContext):
#     commands = l10n.format_value("main-btn").split("\n")
#     if not message.text in commands:
#         await message.answer(l10n.format_value("unknown-message"))
#         return
#
#     await message.answer(l10n.format_value("in-dev"))

# try:
#     em_db = await db.get_user_for_tg_id(message.from_user.id, "em")
#     em_client = await StudentClient(
#         login=str(em_db.login),
#         password=str(em_db.password),
#         localization=em_db.localization,
#     ).init()
#
#
# except InvalidLoginOrPassword:
#     await message.answer(l10n.format_value("incorrect-login-or-password-msg"))
#     await message.answer(l10n.format_value("re-registration-msg"))
#     # await state.set_state(st.Registration.login)
#     # await message.answer(l10n.format_value("enter-login-msg"))
#
# except UnknownError as e:
#     await message.answer(
#         l10n.format_value(
#             "unknown-error-msg",
#             {
#                 "time": str(e.args[2] or "not set"),
#                 "exceptClass": str(e.args[1].__class__.__name__),
#             },
#         )
#     )
#     raise e.args[1]


@router.callback_query(F.data == "get_recent_marks")
async def get_recent_marks(callback: CallbackQuery, l10n: FluentLocalization, em_client: StudentClient):
    await em_client.init()
    dates: dict[str, list[UserStartPageInitialState.UserMarks.Child.Mark]] = {}
    result = ""
    for mark in await em_client.get_recent_marks():
        date = mark.date.astimezone(timezone(timedelta(hours=5), "Tashkent")).strftime(
            "%d.%m.%Y"
        )
        if not dates.get(date):
            dates[date] = []
        dates[date].append(mark)

    for time, marks in dates.items():
        text = l10n.format_value("marks-text", {"time": time}) + "\n<blockquote>"
        for m in marks:
            max_value = "/" + m.marks[0].max_value if m.marks[0].max_value else ""
            text += f"{mood_to_emoji(m.marks[0].mood)}{m.subject.name}: {m.marks[0].value}{max_value} ({m.short_mark_type_text})\n"

        result += text + "</blockquote>\n"

    await callback.answer()
    await callback.message.answer(result)


@router.callback_query(F.data == "get_marks")
async def get_marks(callback: CallbackQuery, l10n: FluentLocalization, em_client: StudentClient):
    now = datetime.now()
    await callback.message.answer(l10n.format_value("date-select-msg"),
                                  reply_markup=kb_inline.create_calendar("mark", now.year, now.month, l10n))

    await callback.answer()


@router.callback_query(F.data.startswith("mark:calendar:"))
async def cb_calendar(callback: CallbackQuery, l10n: FluentLocalization):
    _, year, month = callback.data.split(":")
    year, month = int(year), int(month)
    await callback.message.edit_text(
        "Выберите дату",
        reply_markup=kb_inline.create_calendar("mark", year, month, l10n)
    )


@router.callback_query(F.data.startswith("mark:day:"))
async def cb_day(callback: CallbackQuery, l10n: FluentLocalization, em_client: StudentClient):
    _, _, year, month, day = callback.data.split(":")
    date = datetime(int(year), int(month), int(day))
    await callback.message.edit_text(l10n.format_value("date-selected-msg", {"date": date.strftime('%d.%m.%Y')}))

    try:
        await em_client.init()
        days = await em_client.get_marks(int(date.timestamp()),
                                         int(date.timestamp() + timedelta(days=1).total_seconds()))

        if not days:
            await callback.message.answer(l10n.format_value("no-marks-msg"))

        result = ""
        marks = {}
        for day in days:
            result += f"\n{l10n.format_value("marks-text", {"time": day.date.strftime('%d.%m.%Y')})}\n"

            for lesson in sorted(day.lessons, key=lambda x: x.number):
                for mark in lesson.work_marks:
                    try:
                        marks[lesson.subject.name].append(mark)
                    except KeyError:
                        marks[lesson.subject.name] = [mark]

        for subject, markss in marks.items():
            result += f"<blockquote>{subject}: "
            text = ""
            for mark in markss:
                for m in mark["marks"]:
                    text += f"{mood_to_emoji(m["mood"])}{m["value"]} "
            result += text + "</blockquote>"

        await callback.message.edit_text(result)

    except UnknownError as e:
        await callback.message.answer(l10n.format_value("unknown-error-msg",
                                                {
                                                    "time": str(e.args[2] or "not set"),
                                                    "exceptClass": str(e.args[1].__class__.__name__)
                                                }))
        await callback.message.answer(l10n.format_value("re-registration-msg"))
        raise e.args[1]

    finally:
        await callback.answer("")
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


# === Команда /calendar ===
@router.message(Command("calendar"))
async def cmd_calendar(message: Message, l10n: FluentLocalization):
    now = datetime.now()
    await message.answer("Выберите дату", reply_markup=kb_inline.create_calendar(now.year, now.month, l10n))


# === Перелистывание месяцев ===
@router.callback_query(F.data.startswith("calendar:"))
async def cb_calendar(callback: CallbackQuery, l10n: FluentLocalization):
    _, year, month = callback.data.split(":")
    year, month = int(year), int(month)
    await callback.message.edit_text(
        "Выберите дату",
        reply_markup=kb_inline.create_calendar(year, month, l10n)
    )


# === Выбор конкретного дня ===
@router.callback_query(F.data.startswith("day:"))
async def cb_day(callback: CallbackQuery):
    _, year, month, day = callback.data.split(":")
    date = datetime(int(year), int(month), int(day))
    await callback.message.edit_text(f"✅ Вы выбрали дату: {date.strftime('%d.%m.%Y')}")


# === Игнорируем неактивные кнопки ===
@router.callback_query(F.data == "ignore")
async def cb_ignore(callback: CallbackQuery):
    await callback.answer()
