import validators
from telegram import Update
from telegram.ext import ContextTypes

from handlers import songs, url


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message or update.edited_message
    assert message is not None
    text = message.text
    assert text is not None

    if validators.url(text):
        await url.download_handler(update, context)
    else:
        await songs.search_handler(update, context)
