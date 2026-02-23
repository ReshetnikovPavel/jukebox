from telegram.constants import ParseMode
from typing import Any
import asyncio
import typing

import ytmusicapi
from telegram import Update
from telegram.ext import ContextTypes
from ytmusicapi.models import Lyrics

import consts
import utils


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

    lyrics_id = watch_playlist["lyrics"]
    if lyrics_id is None:
        await context.bot.send_message(chat.id, "У этого трека нет слов в источнике 😭")
        return
    assert isinstance(lyrics_id, str)

    lyrics = await asyncio.to_thread(ytmusic.get_lyrics, lyrics_id, timestamps=False)
    if lyrics is None:
        await context.bot.send_message(chat.id, "У этого трека нет слов в источнике 😭")
        return
    lyrics = typing.cast(Lyrics, lyrics)["lyrics"]

    track = typing.cast(list[dict[str, Any]], watch_playlist["tracks"])[0]
    title = str(track["title"])
    artists = [str(artist["name"]) for artist in track["artists"]]
    artists = ", ".join(artists)

    text = f"<b>{artists} {consts.SEP} {title}</b>\n\n{lyrics}"
    await utils.send_long_message(context.bot, chat.id, text, parse_mode=ParseMode.HTML)
