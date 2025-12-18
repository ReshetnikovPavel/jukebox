import yt
from track import into_track
import logging
from telegram.ext import ContextTypes
from telegram import Update
import yt_dlp
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
    track = into_track(ytmusic.search(video_id, filter="songs", limit=1)[0])

    link = f"https://www.youtube.com/watch?v={video_id}"

    with tempfile.TemporaryDirectory() as tmp_dir:
        out_path = os.path.join(tmp_dir, f"{video_id}.mp3")
        opts = {
            "extract_audio": True,
            "format": "bestaudio",
            "outtmpl": out_path,
        }
        with yt_dlp.YoutubeDL(opts) as video:
            video.download(link)

        await context.bot.send_audio(
            chat.id, out_path, title=track.title, performer=", ".join(track.artists)
        )
