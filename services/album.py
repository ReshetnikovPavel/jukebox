import asyncio
import html
import logging
from dataclasses import dataclass
from typing import Any

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

import consts
import services
from handlers.error import report
from services.yt_cache import CachedYTMusic as YTMusic

Track = dict[str, Any]


@dataclass
class Album:
    tracks: list[tuple[Track, str]]
    artwork: bytes | None


async def get_album(
    ytmusic: YTMusic, browse_id: str, update: Update, context: ContextTypes.DEFAULT_TYPE
) -> Album:
    album = await asyncio.to_thread(ytmusic.get_album, browse_id)
    tracks = album["tracks"]
    video_ids = await asyncio.gather(*[search_video_id(ytmusic, t) for t in tracks])

    try:
        artwork = await services.get_widest_thumbnail(album["thumbnails"])
    except Exception as e:
        await report(e, update, context, "WARN: не получилось найти обложку альбома")
        artwork = None

    return Album(tracks=list(zip(tracks, video_ids)), artwork=artwork)


async def send_album(
    album: Album, browse_id: str, artists_title_str: str, bot: Bot, chat_id: int
) -> None:
    keyboard = [
        [
            InlineKeyboardButton(
                f"{', '.join(a['name'] for a in t['artists'])} {consts.SEP} {t['title']}",
                callback_data=f"{consts.SONG_DOWNLOAD} {video_id} {browse_id}",
            )
        ]
        for (t, video_id) in album.tracks
    ]
    keyboard.append(
        [
            InlineKeyboardButton(
                "Скачать весь альбом",
                callback_data=f"{consts.ALBUM_DOWNLOAD} {browse_id}",
            )
        ]
    )
    reply_markup = InlineKeyboardMarkup(keyboard)

    caption = f"<b>{html.escape(artists_title_str)}</b>\n\nВыберите трек"

    if album.artwork:
        await bot.send_photo(
            chat_id,
            album.artwork,
            caption,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML,
        )
    else:
        await bot.send_message(
            chat_id, caption, reply_markup=reply_markup, parse_mode=ParseMode.HTML
        )


async def search_video_id(ytmusic: YTMusic, track_from_album: dict) -> str:
    query = f"{track_from_album['title']} {track_from_album['artists'][0]['name']}"
    tracks = await asyncio.to_thread(ytmusic.search, query, filter="songs")
    for track in tracks:
        if (
            track["title"] == track_from_album["title"]
            and len(track["artists"]) == len(track_from_album["artists"])
            and all(
                t["id"] == a["id"]
                for (t, a) in zip(track["artists"], track_from_album["artists"])
            )
        ):
            return track["videoId"]
    logging.warning(
        f"Unable to find videoId for track from album TRACK_FROM_ALBUM:::{track_from_album}, TRACKS:::{tracks}"
    )
    return track_from_album["videoId"]
