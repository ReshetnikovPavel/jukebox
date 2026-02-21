import html
import json
import logging
import os
import traceback

from telegram import Update, Chat
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

import consts


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    assert isinstance(context.error, Exception)
    logging.error("Error:", exc_info=context.error)

    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)[:500]

    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        "An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False)[:500])}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data)[:500])}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data)[:500])}</pre>\n\n"
        f"<pre>{html.escape(tb_string[:500])}</pre>"
    )

    if len(message) > 4096:
        message = "An exception was raised while handling an update but the message is too long"

    if developer_chat_id := os.environ.get(consts.DEVELOPER_CHAT_ID_VAR):
        await context.bot.send_message(
            chat_id=developer_chat_id, text=message, parse_mode=ParseMode.HTML
        )
    else:
        logging.error(
            f"Unable to send error message to developer. {consts.DEVELOPER_CHAT_ID_VAR} environment var is not set"
        )

    if isinstance(update, Update) and isinstance(update.effective_chat, Chat):
        chat_id = update.effective_chat.id
        await context.bot.send_message(
            chat_id, "Произошла какая-то ошибка, простите 😭"
        )
