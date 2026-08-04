import json
import logging
import asyncio

import ytmusicapi
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

import consts
import services
import utils

SEARCH_LIMIT = 10


async def search_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> str | int:
    chat = update.effective_chat
    assert chat is not None

    message = update.message or update.edited_message
    assert message is not None

    text = message.text
    assert text is not None
    _command, query = utils.split_command(text)

    ytmusic = ytmusicapi.YTMusic(consts.YT_MUSIC_HEADERS_PATH)
    if not query:
        has_reply = utils.get_performer_and_title_from_reply(message)
        if not has_reply:
            await message.reply_text(
                "Напишите, пожалуйста, ваш запрос\n\nИспользуйте /cancel для отмены"
            )
            return consts.CONVERSATION_HANDLER_REPEAT

        performer, track_title = has_reply
        query = f"{performer} {track_title}"

    artists = await asyncio.to_thread(ytmusic.search, query, filter="artists")
    print(artists)
    if len(artists) == 1 and artists[0]["artist"] == performer:
        await services.get_and_send_artist(
            ytmusic, artists[0]["browseId"], chat.id, context
        )
        return ConversationHandler.END

    artists = artists[:SEARCH_LIMIT]
    if len(artists) == 0:
        await message.reply_text("Ничего не нашлось 😭")
        return ConversationHandler.END

    keyboard = [
        [
            InlineKeyboardButton(
                a["artist"],
                callback_data=f"{consts.ARTIST_GET} {a['browseId']}",
            )
        ]
        for a in artists
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text("Выберите исполнителя", reply_markup=reply_markup)

    return ConversationHandler.END
