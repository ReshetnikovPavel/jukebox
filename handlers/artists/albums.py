import asyncio

import ytmusicapi
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import consts


async def albums_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    assert chat is not None

    callback_query = update.callback_query
    assert callback_query is not None

    callback_data = callback_query.data
    assert callback_data is not None

    artist_id = callback_data.rsplit(maxsplit=1)[1]

    ytmusic = ytmusicapi.YTMusic(consts.YT_MUSIC_HEADERS_PATH)
    artist = await asyncio.to_thread(ytmusic.get_artist, artist_id)

    albums = artist["albums"]["results"]
    # if params := artist["albums"].get("params"):
    #     albums = await asyncio.to_thread(ytmusic.get_artist_albums, artist_id, params)

    if len(albums) == 0:
        await context.bot.send_message(chat.id, "Ничего не нашлось 😭")
        return

    keyboard = [
        [
            InlineKeyboardButton(
                f"{', '.join([artist["name"]] + [a['name'] for a in album['artists']])} {consts.SEP} {album['title']}",
                callback_data=f"{consts.ALBUM_GET} {album['browseId']}",
            )
        ]
        for album in albums
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat.id, "Выберите альбом", reply_markup=reply_markup)
