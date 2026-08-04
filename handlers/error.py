import html
import json
import logging
import os
import traceback
from io import BytesIO

from telegram import Chat, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

import consts


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    assert isinstance(context.error, Exception)
    await report(context.error, update, context)
    if isinstance(update, Update) and isinstance(update.effective_chat, Chat):
        chat_id = update.effective_chat.id
        await context.bot.send_message(
            chat_id, "Произошла какая-то ошибка, простите 😭"
        )


async def report(
    error: Exception,
    update: Update | object,
    context: ContextTypes.DEFAULT_TYPE,
    msg: str | None = None,
) -> None:
    logging.error("Error:", exc_info=error)

    tb_list = traceback.format_exception(None, error, error.__traceback__)
    tb_string = "".join(tb_list)[:500]

    update_str = (
        json.dumps(update.to_dict(), ensure_ascii=False)
        if isinstance(update, Update)
        else str(update)
    )
    message = (
        (msg if msg else "An exception was raised while handling an update\n")
        + f"<pre>update = {html.escape(update_str[:500])}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data)[:500])}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data)[:500])}</pre>\n\n"
        f"<pre>{html.escape(tb_string[-500:])}</pre>"
    )

    if len(message) > 4096:
        message = "An exception was raised while handling an update but the message is too long"

    if developer_chat_id := os.environ.get(consts.DEVELOPER_CHAT_ID_VAR):
        await context.bot.send_message(
            chat_id=developer_chat_id, text=message, parse_mode=ParseMode.HTML
        )

        update_file = BytesIO(update_str.encode())
        update_file.name = "Update.txt"
        await context.bot.send_document(developer_chat_id, update_file)

        error_file = BytesIO("\n".join(traceback.format_exception(error)).encode())
        error_file.name = "Error.txt"
        await context.bot.send_document(developer_chat_id, error_file)
    else:
        logging.error(
            f"Unable to send error message to developer. {consts.DEVELOPER_CHAT_ID_VAR} environment var is not set"
        )
