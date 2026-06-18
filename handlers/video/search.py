import asyncio

import yt_dlp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

import consts
import utils

SEARCH_LIMIT = 10


async def search_handler(
    update: Update, _context: ContextTypes.DEFAULT_TYPE
) -> str | int:
    message = update.message or update.edited_message
    assert message is not None

    text = message.text
    assert text is not None
    _command, query = utils.split_command(text)

    if not query:
        has_reply = utils.get_performer_and_title_from_reply(message)
        if not has_reply:
            await message.reply_text("Напишите, пожалуйста, ваш запрос")
            return consts.CONVERSATION_HANDLER_REPEAT
        performer, title = has_reply
        query = f"{performer} {title}"

    opts = {"extract_flat": "in_playlist", **utils.default_yt_dlp_opts()}
    with yt_dlp.YoutubeDL(opts) as ytdl:
        assert isinstance(ytdl, yt_dlp.YoutubeDL)
        response = await asyncio.to_thread(
            ytdl.extract_info, f"ytsearch{SEARCH_LIMIT}:{query}", download=False
        )

    if len(response["entries"]) == 0:
        await message.reply_text("Ничего не нашлось 😭")
        return ConversationHandler.END

    keyboard = [
        [
            InlineKeyboardButton(
                f"{video['channel']} {consts.SEP} {video['title']}",
                callback_data=f"{consts.SEARCH_CALLBACK_VIDEO} {video['id']}",
            )
        ]
        for video in response["entries"]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text("Выберите трек", reply_markup=reply_markup)

    return ConversationHandler.END
