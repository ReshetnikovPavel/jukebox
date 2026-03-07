from telegram import Update
from telegram.ext import ContextTypes


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    assert chat is not None

    text = """
Что я умею?

- Напишите сообщение без команды, чтобы найти и скачать трек
- Отправьте ссылку чтобы скачать по ней аудио
- Напишите команду /video чтобы найти видео на Youtube и скачать его аудио
- Напишите команду /lyrics чтобы найти текст песни
- Напишите команду /help чтобы получить это сообщение

Например:
    never gonna give you up - я отправлю список треков для скачивания
    https://www.youtube.com/watch?v=dQw4w9WgXcQ - я скачаю аудио с видео
    /video never gonna give you up - я отправлю список видео на Youtube
    /video - я попрошу тебя отправить мне запрос ответ, чтобы дальше найти видео
"""
    await context.bot.send_message(chat.id, text, disable_web_page_preview=True)
