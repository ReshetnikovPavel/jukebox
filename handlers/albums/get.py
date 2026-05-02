import asyncio
import html
import logging

import ytmusicapi
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

import consts
import utils


async def get_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    assert chat is not None

    callback_query = update.callback_query
    assert callback_query is not None

    callback_data = callback_query.data
    assert callback_data is not None

    browse_id = callback_data.split(maxsplit=1)[1]
    artists_title_str = utils.get_selected_button_text(callback_query, browse_id)
    assert artists_title_str is not None

    ytmusic = ytmusicapi.YTMusic(consts.YT_MUSIC_HEADERS_PATH)
    result = await asyncio.to_thread(ytmusic.get_album, browse_id)
    tracks = result["tracks"]
    video_ids = await asyncio.gather(*[search_video_id(ytmusic, t) for t in tracks])

    keyboard = [
        [
            InlineKeyboardButton(
                f"{', '.join(a['name'] for a in t['artists'])} {consts.SEP} {t['title']}",
                callback_data=f"{consts.GET_CALLBACK_ALBUMS} {video_id}",
            )
        ]
        for (t, video_id) in zip(tracks, video_ids)
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
    await context.bot.send_message(
        chat.id, text, reply_markup=reply_markup, parse_mode=ParseMode.HTML
    )


async def search_video_id(ytmusic: ytmusicapi.YTMusic, track_from_album: dict) -> str:
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
