from telegram import Update
from telegram.ext import ContextTypes

from .help import help_handler

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    assert chat is not None

    text = "Привет! Я Jukebox - бот для поиска музыки!"
    await context.bot.send_message(chat.id, text)
    await help_handler(update, context)
