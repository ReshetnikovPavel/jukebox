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
            await message.reply_text("Напишите, пожалуйста, ваш запрос")
            return consts.CONVERSATION_HANDLER_REPEAT

        performer, track_title = has_reply
        query = f"{performer} {track_title}"
        tracks = await asyncio.to_thread(ytmusic.search, query, filter="songs")

        if track := utils.get_song_from_search_response(tracks, performer, track_title):
            album = track["album"]
            album_id = album["id"]
            album_title = album["name"]
            album = await services.get_album(ytmusic, album_id)
            artists_title_str = f"{performer} {consts.SEP} {album_title}"
            await services.send_album(
                album, album_id, artists_title_str, context.bot, chat.id
            )
            return ConversationHandler.END

    albums = await asyncio.to_thread(
        ytmusic.search, query, filter="albums", limit=SEARCH_LIMIT
    )
    albums = albums[:SEARCH_LIMIT]

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
