from datetime import datetime, timezone, timedelta

import structlog
from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, CallbackQuery, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder

from fluent.runtime import FluentLocalization

from filters.is_registered import IsRegisteredFilter
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
router.message.filter(F.chat.type == "private", IsRegisteredFilter(is_registered=True))

# Declare logger
logger = structlog.get_logger()