from telegram import Update
from telegram.ext import ContextTypes

import services
import utils


async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    assert chat is not None

    callback_query = update.callback_query
    assert callback_query is not None

    callback_data = callback_query.data
    assert callback_data is not None

    video_id = callback_data.split(maxsplit=1)[1]
    artists_title_str = utils.find_artists_title_str(callback_query, video_id)
    assert artists_title_str is not None

    await services.download_and_send_song(video_id, artists_title_str, update, context)
