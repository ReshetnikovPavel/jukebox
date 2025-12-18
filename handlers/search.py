import yt
from track import Track, into_track
import consts
import logging
from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup


async def search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if message is None:
        logging.error("message is not present in the update {}", update)
        return
    text = message.text
    if text is None:
        logging.error("text is not present in the message {}", message)
        return

    tracks = search(text)
    keyboard = [
        [
            InlineKeyboardButton(
                f"{','.join(t.artists)} - {t.title}",
                callback_data=f"{consts.SEARCH_CALLBACK} {t.video_id}",
            )
        ]
        for t in tracks
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text("Выберите трек", reply_markup=reply_markup)


def search(query: str) -> list[Track]:
    ytmusic = yt.get_ytmusicapi()
    results = ytmusic.search(query, filter="songs", limit=10)
    return [into_track(r) for r in results]
