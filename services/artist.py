import asyncio
import typing

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import consts
import services
from services.yt_cache import CachedYTMusic as YTMusic


async def get_and_send_artist(
    ytmusic: YTMusic, artist_id: str, chat_id: int, context: ContextTypes.DEFAULT_TYPE
):
    artist = await asyncio.to_thread(ytmusic.get_artist, artist_id)

    description = typing.cast(str, artist["description"] or "")
    description = description.split(".", maxsplit=1)[0]
    caption = []
    caption.append(artist['name'])
    if description:
        caption.append("\n\n")
        caption.append(description)
        caption.append(".")
    caption = "".join(caption)

    artwork = await services.get_widest_thumbnail(artist["thumbnails"])

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
            chat_id, artwork, caption, reply_markup=reply_markup
        )
    else:
        await context.bot.send_message(chat_id, caption, reply_markup=reply_markup)
