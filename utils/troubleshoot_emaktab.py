from aiogram import Bot
from aiogram.types import Message, InputFile, FSInputFile
from fluent.runtime import FluentLocalization

import EmaktabAPI.exceptions as exc
from EmaktabAPI import Client, StudentClient, TeacherClient
from config_reader import BotConfig, get_config


bot_config: BotConfig = get_config(model=BotConfig, root_key="bot")


async def send2admin(bot: Bot, msg: str, chat_id: int = bot_config.chat_id_for_logs, file: InputFile = None):
    if not file:
        await bot.send_message(chat_id=chat_id, text=msg)
        return
    await bot.send_document(chat_id=chat_id, caption=msg, document=file)


async def troubleshoot_emaktab_client(
        client: Client | StudentClient | TeacherClient,
        message: Message,
        l10n: FluentLocalization
):
    bot: Bot = message.bot
    try:
        await client.init()
        return True

    except exc.BadStatusCode as e:
        await send2admin(bot, f"{e.__class__.__name__}: {str(e.args[0])}")
        await message.answer(l10n.format_value("error-bad-code-msg", {"status_code": str(e.args[0])}))

    except exc.NoAuth as e:
        await send2admin(bot, f"{e.__class__.__name__}: {str(e.args[0])}", file=FSInputFile(e.args[1]))
        await message.answer(l10n.format_value("error-no-auth-msg"))

    except exc.UnknownError as e:
        await send2admin(bot, f"{e.args[1].__class__.__name__}", file=FSInputFile(e.args[3]))
        await message.answer(l10n.format_value("error-unknown-msg"))

    except exc.InvalidLoginOrPassword as e:
        raise e
