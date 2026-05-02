import asyncio
import os
import subprocess
import tempfile

import yt_dlp
from telegram import Update
from telegram.ext import ContextTypes

import consts
import handlers
import utils
from services.metadata import write_metadata


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

    link = f"https://music.youtube.com/watch?v={video_id}"
    filename_without_ext = artists_title_str.replace(consts.SEP, "-")
    with tempfile.TemporaryDirectory() as tmp_dir:
        webm_path = os.path.join(tmp_dir, f"{filename_without_ext}.webm")
        opts = {
            "extract_audio": True,
            "format": "bestaudio",
            "outtmpl": webm_path,
            **utils.default_yt_dlp_opts(),
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ytdl:
                await asyncio.to_thread(ytdl.download, link)
        except yt_dlp.DownloadError as e:
            await handlers.error.report(e, update, context)
            del opts["cookiefile"]
            with yt_dlp.YoutubeDL(opts) as ytdl:
                await asyncio.to_thread(ytdl.download, link)
        mp3_path = os.path.join(tmp_dir, f"{filename_without_ext}.mp3")
        audio_path = mp3_path
        subprocess.check_call(["ffmpeg", "-i", webm_path, mp3_path])
        try:
            await write_metadata(video_id, mp3_path)
        except Exception as e:
            await context.bot.send_message(chat.id, "Аудио загрузилось, но не получилось записать метадату 😭")
            await handlers.error.report(e, update, context)

        artists, title = artists_title_str.split(consts.SEP, maxsplit=1)
        artists = artists.strip()
        title = title.strip()
        await context.bot.send_audio(
            chat.id, audio_path, title=title, performer=artists, write_timeout=3600
        )
        await download_message.delete()
