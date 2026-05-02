import asyncio
import html
import typing
from typing import Any

import ytmusicapi
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

import consts
import services
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

    track = typing.cast(list[dict[str, Any]], watch_playlist["tracks"])[0]
    artists = [str(artist["name"]) for artist in track["artists"]]
    artists = ", ".join(artists)
    title = str(track["title"])
    artists_title_str = f"{artists} {consts.SEP} {title}"

    lyrics = await services.get_lyrics(ytmusic, watch_playlist)
    if lyrics is None:
        await context.bot.send_message(
            chat.id,
            f"У <b>{html.escape(artists_title_str)}</b> нет слов в источнике 😭",
            parse_mode=ParseMode.HTML,
        )
        return
    assert isinstance(lyrics, str)

    text = f"<b>{html.escape(artists_title_str)}</b>\n\n{html.escape(lyrics)}"
    await utils.send_long_message(context.bot, chat.id, text, parse_mode=ParseMode.HTML)
