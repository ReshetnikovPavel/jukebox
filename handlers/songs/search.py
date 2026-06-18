import asyncio

import ytmusicapi
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
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
    chat = update.effective_chat
    assert chat is not None

    message = update.message or update.edited_message
    assert message is not None

    text = message.text
    assert text is not None
    _command, query = utils.split_command(text)

    performer = None
    title = None
    if not query:
        has_reply = utils.get_performer_and_title_from_reply(message)
        if not has_reply:
            await message.reply_text("Напишите, пожалуйста, ваш запрос")
            return consts.CONVERSATION_HANDLER_REPEAT
        performer, title = has_reply
        query = f"{performer} {title}"

    ytmusic = ytmusicapi.YTMusic(consts.YT_MUSIC_HEADERS_PATH)
    tracks = await asyncio.to_thread(ytmusic.search, query, filter="songs")

    if performer and title and (track := utils.get_song_from_search_response(tracks, performer, title)):
        video_id = track["videoId"]
        match callback_const:
            case consts.SEARCH_CALLBACK:
                await services.download_and_send_track(
                    video_id, update, context, chat.id, artist=performer, title=title
                )
            case consts.SEARCH_CALLBACK_LYRICS:
                lyrics = await services.get_lyrics_from_video_id(ytmusic, video_id)
                await services.send_lyrics(
                    lyrics, performer, title, context.bot, chat.id
                )
            case _:
                raise Exception("Unsupported callback_const", callback_const)
        return ConversationHandler.END

    tracks = tracks[:SEARCH_LIMIT]
    if len(tracks) == 0:
        await message.reply_text("Ничего не нашлось 😭")
        return ConversationHandler.END

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
    return ConversationHandler.END


async def search_lyrics_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await search_handler(
        update, context, callback_const=consts.SEARCH_CALLBACK_LYRICS
    )
