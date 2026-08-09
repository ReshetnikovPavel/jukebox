import utils
import importlib
import logging
import os

from telegram import Update
from telegram.ext import ContextTypes

import consts


async def migration_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    assert chat is not None

    username = chat.username
    assert username is not None

    developer_chat_id = os.environ.get(consts.DEVELOPER_CHAT_ID_VAR)
    if developer_chat_id is None:
        logging.error(f"{consts.DEVELOPER_CHAT_ID_VAR} environment var is not set")
        return
    developer_chat_id = int(developer_chat_id)
    
    if chat.id != developer_chat_id:
        raise Exception(f"{username} tried to access /migrate command")

    message = update.message or update.edited_message
    assert message is not None

    text = message.text
    assert text is not None
    _command, module = utils.split_command(text)

    if not all(c.isalnum() or c == "_" for c in module):
        raise Exception(f"module name must be alphanumeric or _")

    migration = importlib.import_module(f"migrations.{module}")
    await migration.migrate(update, context)
