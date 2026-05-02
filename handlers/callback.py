from telegram import Update
from telegram.ext import ContextTypes

import consts
from handlers import albums, songs


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    callback_query = update.callback_query
    assert callback_query is not None

    callback_data = callback_query.data
    assert callback_data is not None

    await callback_query.answer()

    parts = callback_data.split()
    command = parts[0]
    match command:
        case consts.SEARCH_CALLBACK:
            return await songs.download_handler(update, context)
        case consts.SEARCH_CALLBACK_LYRICS:
            return await songs.get_lyrics_handler(update, context)
        case consts.SEARCH_CALLBACK_ALBUMS:
            return await albums.get_handler(update, context)
        case consts.GET_CALLBACK_ALBUMS:
            return await albums.download_handler(update, context)
        case _:
            raise Exception("Unknown callback_data", callback_data)
