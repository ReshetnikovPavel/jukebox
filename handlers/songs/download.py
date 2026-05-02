import asyncio
from telegram import Update
from telegram.ext import ContextTypes

import consts
import handlers
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

    metadata_task = asyncio.create_task(services.get_metadata_by_video_id(video_id, browse_id))
    async with services.download_song(
        video_id, artists_title_str, update, context
    ) as audio_path:
        try:
            metadata = await metadata_task
            services.write_metadata(metadata, audio_path)
        except Exception as e:
            await context.bot.send_message(
                chat.id, "Аудио загрузилось, но не получилось записать метадату 😭"
            )
            await handlers.error.report(e, update, context)

        artists, title = artists_title_str.split(consts.SEP, maxsplit=1)
        artists = artists.strip()
        title = title.strip()
        await context.bot.send_audio(
            chat.id, audio_path, title=title, performer=artists, write_timeout=3600
        )
