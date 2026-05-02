import asyncio
import json
import os
import tempfile
from urllib.parse import parse_qs, urlparse

import validators
import yt_dlp
from telegram import Update
from telegram.ext import ContextTypes
from yt_dlp.utils import DownloadError

import handlers
import services
import utils


async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    assert chat is not None

    message = update.message or update.edited_message
    assert message is not None

    link = message.text
    assert link is not None
    assert validators.url(link)

    parsed_url = urlparse(link)
    domain = parsed_url.netloc
    if domain == "youtube.com" or domain.endswith(".youtube.com"):
        video_id = parse_qs(parsed_url.query)["v"][0]
        await services.download_and_send_track(video_id, update, context, chat.id)
        return
    if domain == "youtu.be":
        video_id = parsed_url.path.split("/")[1]
        await services.download_and_send_track(video_id, update, context, chat.id)
        return

    download_message = await context.bot.send_message(
        chat.id, "Скачиваю аудио из видео"
    )

    with tempfile.TemporaryDirectory() as tmp_dir:
        out_path = os.path.join(tmp_dir, "audio.mp3")
        opts = {
            "extract_audio": True,
            "writeinfojson": True,
            "noplaylist": True,
            "format": "bestaudio",
            "outtmpl": out_path,
            **utils.default_yt_dlp_opts(),
        }

        try:
            with yt_dlp.YoutubeDL(opts) as ytdl:
                await asyncio.to_thread(ytdl.download, link)
        except DownloadError as e:
            await handlers.error.report(e, update, context)
            del opts["cookiefile"]
            with yt_dlp.YoutubeDL(opts) as ytdl:
                await asyncio.to_thread(ytdl.download, link)

        with open(out_path + ".info.json") as metadata_file:
            metadata = json.load(metadata_file)
            title = metadata["title"]
            performer = metadata["uploader"]

        await context.bot.send_audio(
            chat.id, out_path, title=title, performer=performer
        )

    await download_message.delete()
