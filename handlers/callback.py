import logging

from telegram import Update
from telegram.ext import ContextTypes

import consts
import handlers


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    callback_query = update.callback_query
    if callback_query is None:
        logging.error("callback_query is not present in the update {}", update)
        return

    callback_data = callback_query.data
    if callback_data is None:
        logging.error("data is not present in the callback_query {}", update)
        return

    if callback_data.startswith(consts.SEARCH_CALLBACK):
        await handlers.download_handler(update, context, callback_data)
    else:
        logging.error("Unknown callback_data {}", callback_data)
        return
