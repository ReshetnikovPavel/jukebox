import yt_dlp
import asyncio
import logging
import os
import tempfile

from telegram import CallbackQuery, Message, Update
from telegram.ext import ContextTypes

import consts


async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat is None:
        logging.error("effective_chat is not present in the update {}", update)
        return

    callback_query = update.callback_query
    if callback_query is None:
        logging.error("callback_query is not present in the update {}", update)
        return

    callback_data = callback_query.data
    if callback_data is None:
        logging.error("data is not present in the callback_query {}", update)
        return

    video_id = callback_data.split(maxsplit=1)[1]
    artists_title_str = find_artists_title_str(callback_query, video_id)
    if artists_title_str is None:
        logging.error(
            "artists_title_str is not found in callback_query {}", callback_query
        )
        return

    download_message = await context.bot.send_message(
        chat.id, f"Загружаю трек {artists_title_str}"
    )

    link = f"https://www.youtube.com/watch?v={video_id}"
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_path = os.path.join(tmp_dir, f"{artists_title_str}.mp3")
        opts = {
            "extract_audio": True,
            "format": "bestaudio",
            "outtmpl": out_path,
        }
        with yt_dlp.YoutubeDL(opts) as ytdl:
            try:
                await asyncio.to_thread(ytdl.download, link)
            except Exception as e:
                await context.bot.send_message(
                    chat.id, "Почему-то не получилось загрузить песню, простите 😭"
                )
                logging.error("yt_dlp download failed: {}", e)
                return

        artists, title = artists_title_str.split(consts.SEP, maxsplit=1)
        artists = artists.strip()
        title = title.strip()
        await context.bot.send_audio(chat.id, out_path, title=title, performer=artists)
        await download_message.delete()


def find_artists_title_str(callback_query: CallbackQuery, video_id: str) -> str | None:
    message = callback_query.message
    if message is None:
        logging.error("message is not present in the callback_query {}", callback_query)
        return

    if not isinstance(message, Message):
        logging.error("message has unexpected type {}", message)
        return

    reply_markup = message.reply_markup
    if reply_markup is None:
        logging.error("reply_markup is not present in the message {}", message)
        return

    for line in reply_markup.inline_keyboard:
        button = line[0]
        data = button.callback_data
        if not isinstance(data, str):
            logging.error("data has unexpected type {}", data)
            return
        if data.find(video_id) != -1:
            return button.text
