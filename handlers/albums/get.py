import services

import ytmusicapi
from telegram import Update
from telegram.ext import ContextTypes

import consts
import utils


async def get_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    assert chat is not None

    callback_query = update.callback_query
    assert callback_query is not None

    callback_data = callback_query.data
    assert callback_data is not None

    browse_id = callback_data.split(maxsplit=1)[1]
    artists_title_str = utils.get_selected_button_text(callback_query, browse_id)
    assert artists_title_str is not None

    ytmusic = ytmusicapi.YTMusic(consts.YT_MUSIC_HEADERS_PATH)
    album = await services.get_album(ytmusic, browse_id)
    await services.send_album(album, browse_id, artists_title_str, context.bot, chat.id)
