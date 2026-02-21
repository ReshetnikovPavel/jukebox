import ytmusicapi
import asyncio

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import consts
from track import into_track


async def search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    assert message is not None

    text = message.text
    assert text is not None

    ytmusic = ytmusicapi.YTMusic(consts.YT_MUSIC_HEADERS_PATH)
    results = await asyncio.to_thread(ytmusic.search, text, filter="songs", limit=10)
    tracks = [into_track(r) for r in results]

    keyboard = [
        [
            InlineKeyboardButton(
                f"{', '.join(t.artists)} {consts.SEP} {t.title}",
                callback_data=f"{consts.SEARCH_CALLBACK} {t.video_id}",
            )
        ]
        for t in tracks
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text("Выберите трек", reply_markup=reply_markup)
