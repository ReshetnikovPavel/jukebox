import asyncio
import typing
from typing import Any

import ytmusicapi
from telegram import Update
from telegram.ext import ContextTypes

import consts
import services


async def get_lyrics_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    assert chat is not None

    callback_query = update.callback_query
    assert callback_query is not None

    callback_data = callback_query.data
    assert callback_data is not None

    video_id = callback_data.split(maxsplit=1)[1]
    ytmusic = ytmusicapi.YTMusic(consts.YT_MUSIC_HEADERS_PATH)

    watch_playlist = await asyncio.to_thread(
        ytmusic.get_watch_playlist, video_id, limit=1
    )

    track = typing.cast(list[dict[str, Any]], watch_playlist["tracks"])[0]
    artists = [str(artist["name"]) for artist in track["artists"]]
    artists = ", ".join(artists)
    title = str(track["title"])

    lyrics = await services.get_lyrics_from_playlist(ytmusic, watch_playlist)
    await services.send_lyrics(lyrics, artists, title, context.bot, chat.id)
