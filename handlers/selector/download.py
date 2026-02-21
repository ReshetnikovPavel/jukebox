import yt_dlp
import asyncio
import os
import tempfile

from telegram import CallbackQuery, Message, Update
from telegram.ext import ContextTypes

import consts


async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    assert chat is not None

    callback_query = update.callback_query
    assert callback_query is not None

    callback_data = callback_query.data
    assert callback_data is not None

    video_id = callback_data.split(maxsplit=1)[1]
    artists_title_str = find_artists_title_str(callback_query, video_id)
    assert artists_title_str is not None

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
            await asyncio.to_thread(ytdl.download, link)

        artists, title = artists_title_str.split(consts.SEP, maxsplit=1)
        artists = artists.strip()
        title = title.strip()
        await context.bot.send_audio(chat.id, out_path, title=title, performer=artists)
        await download_message.delete()


def find_artists_title_str(callback_query: CallbackQuery, video_id: str) -> str | None:
    message = callback_query.message
    assert message is not None
    assert isinstance(message, Message)

    reply_markup = message.reply_markup
    assert reply_markup is not None

    for line in reply_markup.inline_keyboard:
        button = line[0]
        data = button.callback_data
        assert isinstance(data, str)

        if data.find(video_id) != -1:
            return button.text
