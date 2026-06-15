import asyncio
from typing import Any

import ytmusicapi
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Message, Update
from telegram.ext import ContextTypes, ConversationHandler

import consts
import services
import utils

SEARCH_LIMIT = 10


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

    ytmusic = ytmusicapi.YTMusic(consts.YT_MUSIC_HEADERS_PATH)
    tracks = await asyncio.to_thread(
        ytmusic.search, text, filter="songs", limit=SEARCH_LIMIT
    )
    tracks = tracks[:SEARCH_LIMIT]
    await __send_search_table(tracks, message, callback_const)
    return ConversationHandler.END


async def __send_search_table(
    tracks: list[dict[str, Any]], message: Message, callback_const: str
) -> None:
    if len(tracks) == 0:
        await message.reply_text("Ничего не нашлось 😭")
        return

    keyboard = [
        [
            InlineKeyboardButton(
                f"{', '.join(a['name'] for a in t['artists'])} {consts.SEP} {t['title']}",
                callback_data=f"{callback_const} {t['videoId']}",
            )
        ]
        for t in tracks
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text("Выберите трек", reply_markup=reply_markup)


async def search_lyrics_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    assert chat is not None

    message = update.message or update.edited_message
    assert message is not None

    text = message.text
    assert text is not None
    command, text = utils.split_command(text)

    if not text or text.isspace():
        if await __try_to_find_and_send_lyrics_from_audio_reply(
            message, context.bot, chat.id, consts.SEARCH_CALLBACK_LYRICS
        ):
            return ConversationHandler.END

    return await search_handler(
        update, context, callback_const=consts.SEARCH_CALLBACK_LYRICS
    )


async def __try_to_find_and_send_lyrics_from_audio_reply(
    message: Message, bot: Bot, chat_id: int, callback_const: str
) -> bool:
    reply = message.reply_to_message
    if reply is None:
        return False
    audio = reply.audio
    if audio is None:
        return False
    title = audio.title
    if title is None:
        return False
    performer = audio.performer
    if performer is None:
        return False

    ytmusic = ytmusicapi.YTMusic(consts.YT_MUSIC_HEADERS_PATH)
    tracks = await asyncio.to_thread(
        ytmusic.search, f"{title} {performer}", filter="songs", limit=SEARCH_LIMIT
    )

    artists = set(performer.split(", "))
    video_id = None
    for track in tracks:
        track_artists = {a["name"] for a in track["artists"]}
        if track["title"] == title and track_artists == artists:
            video_id = track["videoId"]
            break

    if video_id is not None:
        lyrics = await services.get_lyrics_from_video_id(ytmusic, video_id)
        await services.send_lyrics(lyrics, performer, title, bot, chat_id)
        return True

    tracks = tracks[:SEARCH_LIMIT]
    await __send_search_table(tracks, message, callback_const)
    return True
