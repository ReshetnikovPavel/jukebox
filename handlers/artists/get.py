import asyncio
import typing
from typing import Any

import requests
import ytmusicapi
from requests.models import Response
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import consts


async def get_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    assert chat is not None

    callback_query = update.callback_query
    assert callback_query is not None

    callback_data = callback_query.data
    assert callback_data is not None

    artist_id = callback_data.split(maxsplit=1)[1]

    ytmusic = ytmusicapi.YTMusic(consts.YT_MUSIC_HEADERS_PATH)
    artist = await asyncio.to_thread(ytmusic.get_artist, artist_id)

    description = typing.cast(str, artist["description"])
    description = description.split(".", maxsplit=1)[0]
    caption = f"{artist['name']}\n\n{description}."

    artwork = await __get_artwork(artist["thumbnails"])

    keyboard = []
    if len(artist["songs"]["results"]) > 0:
        first_song_id = artist["songs"]["results"][0]["videoId"]
        keyboard.append(
            [
                InlineKeyboardButton(
                    "Треки",
                    callback_data=f"{consts.ARTIST_SONGS} {artist_id} {first_song_id}",
                )
            ]
        )
    if len(artist["albums"]["results"]) > 0:
        keyboard.append(
            [
                InlineKeyboardButton(
                    "Альбомы",
                    callback_data=f"{consts.ARTIST_ALBUMS} {artist_id}",
                )
            ]
        )

    reply_markup = InlineKeyboardMarkup(keyboard)
    if artwork:
        await context.bot.send_photo(
            chat.id, artwork, caption, reply_markup=reply_markup
        )
    else:
        await context.bot.send_message(chat.id, caption, reply_markup=reply_markup)


async def __get_artwork(thumbnails: list[dict[str, Any]]) -> bytes | None:
    widest_thumbnail = max(thumbnails, key=lambda t: t["width"], default=None)
    if widest_thumbnail is None:
        return None

    url = widest_thumbnail["url"]
    image_response = await asyncio.to_thread(requests.get, url)
    image_response = typing.cast(Response, image_response)
    if not image_response.ok:
        raise Exception("Unable to get artwork", image_response)

    return image_response.content
