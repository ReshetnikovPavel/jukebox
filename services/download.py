import asyncio
import logging
import os
import tempfile

import yt_dlp
from telegram import Update
from telegram.ext import ContextTypes

import consts
import utils


async def download_and_send_song(
    video_id: str,
    artists_title_str: str,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    chat = update.effective_chat
    assert chat is not None

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
            **utils.default_yt_dlp_opts(),
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ytdl:
                await asyncio.to_thread(ytdl.download, link)
        except yt_dlp.DownloadError as e:
            logging.error(e)
            del opts["cookiefile"]
            with yt_dlp.YoutubeDL(opts) as ytdl:
                await asyncio.to_thread(ytdl.download, link)

        artists, title = artists_title_str.split(consts.SEP, maxsplit=1)
        artists = artists.strip()
        title = title.strip()
        await context.bot.send_audio(chat.id, out_path, title=title, performer=artists)
        await download_message.delete()
