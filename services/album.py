import asyncio
import html
import logging
from typing import Any

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from ytmusicapi import YTMusic

import consts

Track = dict[str, Any]
Album = list[tuple[Track, str]]


async def get_album(ytmusic: YTMusic, browse_id: str) -> Album:
    result = await asyncio.to_thread(ytmusic.get_album, browse_id)
    tracks = result["tracks"]
    video_ids = await asyncio.gather(*[search_video_id(ytmusic, t) for t in tracks])

    return list(zip(tracks, video_ids))


async def send_album(
    album: Album, browse_id: str, artists_title_str: str, bot: Bot, chat_id: int
) -> None:
    keyboard = [
        [
            InlineKeyboardButton(
                f"{', '.join(a['name'] for a in t['artists'])} {consts.SEP} {t['title']}",
                callback_data=f"{consts.GET_CALLBACK_ALBUMS} {video_id}",
            )
        ]
        for (t, video_id) in album
    ]
    keyboard.append(
        [
            InlineKeyboardButton(
                "Скачать весь альбом",
                callback_data=f"{consts.GET_CALLBACK_ALBUMS} {browse_id}",
            )
        ]
    )
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"<b>{html.escape(artists_title_str)}</b>\n\nВыберите трек"
    await bot.send_message(
        chat_id, text, reply_markup=reply_markup, parse_mode=ParseMode.HTML
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
