import asyncio
from dataclasses import dataclass

import ytmusicapi
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

import consts
import utils


async def search_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    callback_const=consts.SEARCH_CALLBACK,
) -> str | int:
    message = update.message or update.edited_message
    assert message is not None

    text = message.text
    assert text is not None
    command, text = utils.split_command(text)

    if text == "" or text.isspace():
        await message.reply_text("Напишите, пожалуйста, ваш запрос")
        return consts.CONVERSATION_HANDLER_REPEAT

    limit = 10
    ytmusic = ytmusicapi.YTMusic(consts.YT_MUSIC_HEADERS_PATH)
    results = await asyncio.to_thread(ytmusic.search, text, filter="songs", limit=limit)
    songs = [into_song(r) for r in results[:limit]]

    if len(songs) == 0:
        await message.reply_text("Ничего не нашлось 😭")
        return ConversationHandler.END

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

    return ConversationHandler.END


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
