from telegram import Update
from telegram.ext import ContextTypes

import consts
from handlers import selector


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    callback_query = update.callback_query
    assert callback_query is not None

    callback_data = callback_query.data
    assert callback_data is not None

    await callback_query.answer()

    command = callback_data.split()[0]
    if command == consts.SEARCH_CALLBACK:
        await selector.download_handler(update, context)
    else:
        raise Exception("Unknown callback_data", callback_data)
