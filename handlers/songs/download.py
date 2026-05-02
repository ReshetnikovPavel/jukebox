import consts
from telegram import Update
from telegram.ext import ContextTypes

import services
import utils


async def download_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    browse_id: str | None = None,
):
    chat = update.effective_chat
    assert chat is not None

    callback_query = update.callback_query
    assert callback_query is not None

    callback_data = callback_query.data
    assert callback_data is not None

    video_id = callback_data.split(maxsplit=1)[1]
    artists_title_str = utils.get_selected_button_text(callback_query, video_id)
    assert artists_title_str is not None

    artist, title = artists_title_str.split(consts.SEP, maxsplit=1)
    artist = artist.strip()
    title = title.strip()

    await services.download_and_send_track(
        video_id,
        update,
        context,
        chat.id,
        browse_id=browse_id,
        artist=artist,
        title=title,
    )
