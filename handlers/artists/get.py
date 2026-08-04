import ytmusicapi
from telegram import Update
from telegram.ext import ContextTypes

import consts
import services


async def get_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    assert chat is not None

    callback_query = update.callback_query
    assert callback_query is not None

    callback_data = callback_query.data
    assert callback_data is not None

    artist_id = callback_data.split(maxsplit=1)[1]

    ytmusic = ytmusicapi.YTMusic(consts.YT_MUSIC_HEADERS_PATH)
    await services.get_and_send_artist(ytmusic, artist_id, chat.id, context)
