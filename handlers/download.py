import yt
import logging
from telegram.ext import ContextTypes
from telegram import Update
import tempfile
import os


async def download_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str
):
    chat = update.effective_chat
    if chat is None:
        logging.error("effective_chat is not present in the update {}", update)
        return

    video_id = callback_data.split()[1]

    ytmusic = yt.get_ytmusicapi()
    song = ytmusic.get_song(video_id)

    title = song["videoDetails"]["title"]
    author = song["videoDetails"]["author"]
    author = author.replace(" &", ",")

    link = f"https://www.youtube.com/watch?v={video_id}"
    with tempfile.TemporaryDirectory() as tmp_dir:
        out_path = os.path.join(tmp_dir, f"{video_id}.mp3")
        with yt.get_yt_dlp(out_path) as ytdl:
            ytdl.download(link)

        await context.bot.send_audio(
            chat.id, out_path, title=title, performer=author
        )
