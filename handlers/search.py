import asyncio
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import consts
import yt
from track import into_track


async def search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if message is None:
        logging.error("message is not present in the update {}", update)
        return
    text = message.text
    if text is None:
        logging.error("text is not present in the message {}", message)
        return

    ytmusic = yt.get_ytmusicapi()
    results = await asyncio.to_thread(ytmusic.search, text, filter="songs", limit=10)
    tracks = [into_track(r) for r in results]

    keyboard = [
        [
            InlineKeyboardButton(
                f"{', '.join(t.artists)} – {t.title}",
                callback_data=f"{consts.SEARCH_CALLBACK} {t.video_id}",
            )
        ]
        for t in tracks
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text("Выберите трек", reply_markup=reply_markup)
