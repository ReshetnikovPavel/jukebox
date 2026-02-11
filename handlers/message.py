import logging

import validators
from telegram import Update
from telegram.ext import ContextTypes

from handlers import url, selector

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if message is None:
        logging.error("message is not present in the update {}", update)
        return
    text = message.text
    if text is None:
        logging.error("text is not present in the message {}", message)
        return

    if validators.url(text):
        await url.download_handler(update, context)
    else:
        selector.search_handler(update, context)
