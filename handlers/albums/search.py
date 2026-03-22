import logging
import asyncio

import ytmusicapi
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

import consts
import utils


async def search_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> str | int:
    message = update.message or update.edited_message
    assert message is not None

    text = message.text
    assert text is not None
    command, text = utils.split_command(text)

    if text == "" or text.isspace():
        await message.reply_text("Напишите, пожалуйста, ваш запрос")
        return consts.CONVERSATION_HANDLER_REPEAT

    ytmusic = ytmusicapi.YTMusic(consts.YT_MUSIC_HEADERS_PATH)
    albums = await asyncio.to_thread(ytmusic.search, text, filter="albums", limit=10)
    albums = albums[:10]

    logging.info(albums)
    keyboard = [
        [
            InlineKeyboardButton(
                f"{', '.join(artist['name'] for artist in a['artists'])} {consts.SEP} {a['title']}",
                callback_data=f"{consts.SEARCH_CALLBACK_ALBUMS} {a['browseId']}",
            )
        ]
        for a in albums
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text("Выберите альбом", reply_markup=reply_markup)

    return ConversationHandler.END
