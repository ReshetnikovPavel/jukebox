import logging
from telegram.ext import ContextTypes
from telegram import Update


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat is None:
        logging.error("effective_chat is not present in the update {}", update)
        return

    text = "Привет! Я Jukebox - бот для поиска музыки! Напиши сообщение, а я найду по нему список треков"
    await context.bot.send_message(chat_id=chat.id, text=text)




