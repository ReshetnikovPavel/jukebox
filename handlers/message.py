import validators
from telegram import Update
from telegram.ext import ContextTypes

import consts
from handlers import songs, url, video


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message or update.edited_message
    assert message is not None
    text = message.text
    assert text is not None

    if reply := message.reply_to_message:
        if reply.text is not None:
            if reply.text.endswith(consts.LYRICS_COMMAND):
                return await songs.search_lyrics_handler(update, context)
            elif reply.text.endswith(consts.VIDEO_COMMAND):
                return await video.search_handler(update, context)

    if validators.url(text):
        await url.download_handler(update, context)
    else:
        await songs.search_handler(update, context)
