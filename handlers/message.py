import validators
from telegram import Update
from telegram.ext import ContextTypes

from handlers import url, songs

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    assert message is not None
    text = message.text
    assert text is not None

    if validators.url(text):
        await url.download_handler(update, context)
    else:
        await songs.search_handler(update, context)
