import asyncio
import logging
import os
import tempfile

from telegram import Update
from telegram.ext import ContextTypes

import yt


async def download_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE, video_id: str
):
    chat = update.effective_chat
    if chat is None:
        logging.error("effective_chat is not present in the update {}", update)
        return

    try:
        ytmusic = yt.get_ytmusicapi()
        song = await asyncio.to_thread(ytmusic.get_song, video_id)
    except Exception as e:
        await context.bot.send_message(
            chat.id, "Почему-то не получилось найти песню, простите 😭"
        )
        logging.error("YouTube music get_song failed: {}", e)
        return

    title = song["videoDetails"]["title"]
    author = song["videoDetails"]["author"]
    author = author.replace(" &", ",")

    download_message = await context.bot.send_message(chat.id, f"Загружаю трек {author} – {title}")

    link = f"https://www.youtube.com/watch?v={video_id}"
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_path = os.path.join(tmp_dir, f"{video_id}.mp3")
        with yt.get_yt_dlp(out_path) as ytdl:
            try:
                await asyncio.to_thread(ytdl.download, link)
            except Exception as e:
                await context.bot.send_message(
                    chat.id, "Почему-то не получилось загрузить песню, простите 😭"
                )
                logging.error("yt_dlp download failed: {}", e)
                return

        await context.bot.send_audio(chat.id, out_path, title=title, performer=author)
        await download_message.delete()
