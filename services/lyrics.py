import asyncio
import html
import typing

import ytmusicapi
from telegram import Bot
from telegram.constants import ParseMode
from ytmusicapi.models import Lyrics

import consts
import utils


async def get_lyrics_from_video_id(
    ytmusic: ytmusicapi.YTMusic, video_id: str
) -> str | None:
    watch_playlist = await asyncio.to_thread(
        ytmusic.get_watch_playlist, video_id, limit=1
    )
    return await get_lyrics_from_playlist(ytmusic, watch_playlist)


async def get_lyrics_from_playlist(
    ytmusic: ytmusicapi.YTMusic, watch_playlist: dict
) -> str | None:
    lyrics_id = watch_playlist["lyrics"]
    if lyrics_id is None:
        return None
    assert isinstance(lyrics_id, str)

    lyrics = await asyncio.to_thread(ytmusic.get_lyrics, lyrics_id, timestamps=False)
    if lyrics is None:
        return None
    lyrics = typing.cast(Lyrics, lyrics)["lyrics"]
    return lyrics


async def send_lyrics(
    lyrics: str | None, artists: str, title: str, bot: Bot, chat_id: int
):
    artists_title_str = f"{artists} {consts.SEP} {title}"

    if lyrics is None:
        await bot.send_message(
            chat_id,
            f"У <b>{html.escape(artists_title_str)}</b> нет слов в источнике 😭",
            parse_mode=ParseMode.HTML,
        )
        return
    assert isinstance(lyrics, str)

    text = f"<b>{html.escape(artists_title_str)}</b>\n\n{html.escape(lyrics)}"
    await utils.send_long_message(bot, chat_id, text, parse_mode=ParseMode.HTML)
