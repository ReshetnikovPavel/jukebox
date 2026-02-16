import json
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

    download_message = await context.bot.send_message(chat.id, "Скачиваю аудио из видео")

    with tempfile.TemporaryDirectory() as tmp_dir:
        out_path = os.path.join(tmp_dir, "audio.mp3")
        opts = {
            "extract_audio": True,
            "writeinfojson": True,
            "noplaylist": True,
            "format": "bestaudio",
            "outtmpl": out_path,
        }
        with yt_dlp.YoutubeDL(opts) as ytdl:
            try:
                await asyncio.to_thread(ytdl.download, link)
            except Exception as e:
                await context.bot.send_message(
                    chat.id,
                    "Почему-то не получилось загрузить аудио, простите 😭",
                )
                logging.error("yt_dlp download failed", e)
                return

        with open(out_path + ".info.json") as metadata_file:
            metadata = json.load(metadata_file)
            title = metadata["title"]
            performer = metadata["uploader"]

        await context.bot.send_audio(chat.id, out_path, title=title, performer=performer)

    await download_message.delete()
