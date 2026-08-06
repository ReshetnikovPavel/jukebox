import asyncio
import typing

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import consts
import services
from services.yt_cache import CachedYTMusic as YTMusic

TG_MAX_CAPTION_LEN = 1024


async def get_and_send_artist(
    ytmusic: YTMusic, artist_id: str, chat_id: int, context: ContextTypes.DEFAULT_TYPE
):
    artist = await asyncio.to_thread(ytmusic.get_artist, artist_id)

    description = typing.cast(str, artist["description"] or "")
    description = description.split("\n", maxsplit=1)[0]

    caption = []
    caption.append(artist['name'])
    if description:
        caption.append("\n\n")
        caption.append(description)
    caption = "".join(caption)

    if len(caption) >= TG_MAX_CAPTION_LEN:
        last_dot_index = caption.rfind('.', 0, TG_MAX_CAPTION_LEN)
        if last_dot_index != -1:
            caption = caption[:last_dot_index + 1]
        else:
            caption = caption[:TG_MAX_CAPTION_LEN]


    artwork = await services.get_widest_thumbnail(artist["thumbnails"])

    keyboard = []
    if len(artist["songs"]["results"]) > 0:
        keyboard.append(
            [
                InlineKeyboardButton(
                    "Треки",
                    callback_data=f"{consts.ARTIST_SONGS} {artist_id}",
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
