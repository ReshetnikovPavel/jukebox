from telegram import Update
from telegram.ext import ContextTypes


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    assert chat is not None

    text = "Привет! Я Jukebox - бот для поиска музыки! Напиши сообщение, а я найду по нему список треков"
    await context.bot.send_message(chat.id, text)
