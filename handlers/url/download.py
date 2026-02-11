import yt_dlp
import asyncio
import logging
import os
import tempfile

import validators
from telegram import Update
from telegram.ext import ContextTypes


async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat is None:
        logging.error("effective_chat is not present in the update {}", update)
        return
    message = update.message
    if message is None:
        logging.error("message is not present in the update", update)
        return
    link = message.text
    if link is None:
        logging.error("text is not present in the message", message)
        return

    if not validators.url(link):
        logging.error("A link must be a valid url", link)
        return

    download_message = await context.bot.send_message(
        chat.id, f"Загружаю видео и аудио по ссылке {link}"
    )

    with tempfile.TemporaryDirectory() as tmp_dir:
        opts = {
            "extract_audio": True,
            "keep_video": True,
            "format": "bestvideo+bestaudio",
            "outtmpl": tmp_dir,
        }
        with yt_dlp.YoutubeDL(opts) as ytdl:
            try:
                await asyncio.to_thread(ytdl.download, link)
            except Exception as e:
                await context.bot.send_message(
                    chat.id,
                    "Почему-то не получилось загрузить видео и аудио, простите 😭",
                )
                logging.error("yt_dlp download failed: {}", e)
                return

        file_names = os.listdir(tmp_dir)
        for file_name in file_names:
            if file_name.endswith(".mp3"):
                await context.bot.send_audio(chat.id, os.path.join(tmp_dir, file_name))
            else:
                await context.bot.send_video(chat.id, os.path.join(tmp_dir, file_name))

    await download_message.delete()
