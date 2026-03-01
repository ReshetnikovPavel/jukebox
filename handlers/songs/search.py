from dataclasses import dataclass
import asyncio

import ytmusicapi
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import consts


async def search_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    callback_const=consts.SEARCH_CALLBACK,
):
    message = update.message
    assert message is not None

    text = message.text
    assert text is not None
    if text.startswith("/"):
        splits = text.split(maxsplit=1)
        text = "" if len(splits) == 1 else splits[1]

    if text == "" or text.isspace():
        await message.reply_text("Кажется, что вы забыли написать, что нужно найти 😭")
        return

    ytmusic = ytmusicapi.YTMusic(consts.YT_MUSIC_HEADERS_PATH)
    results = await asyncio.to_thread(ytmusic.search, text, filter="songs", limit=10)
    songs = [into_song(r) for r in results]

    keyboard = [
        [
            InlineKeyboardButton(
                f"{', '.join(t.artists)} {consts.SEP} {t.title}",
                callback_data=f"{callback_const} {t.video_id}",
            )
        ]
        for t in songs
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text("Выберите трек", reply_markup=reply_markup)


async def search_lyrics_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await search_handler(
        update, context, callback_const=consts.SEARCH_CALLBACK_LYRICS
    )


@dataclass()
class Song:
    title: str
    artists: list[str]
    video_id: str


def into_song(data: dict) -> Song:
    title = data["title"]
    artists = [artist["name"] for artist in data["artists"]]
    video_id = data["videoId"]
    return Song(title, artists, video_id)
