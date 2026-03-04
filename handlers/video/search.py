import asyncio

import yt_dlp
from telegram import ForceReply, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import consts
import utils


async def search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    assert message is not None

    text = message.text
    assert text is not None
    command, text = utils.split_command(text)

    if text == "" or text.isspace():
        if command:
            await message.reply_text(
                f"Напишите, пожалуйста, ваш запрос для команды {command}",
                reply_markup=ForceReply(),
            )
        else:
            await message.reply_text(
                "Напишите, пожалуйста, ваш запрос",
                reply_markup=ForceReply(),
            )
        return

    limit = 10
    opts = {"extract_flat": "in_playlist", **utils.default_yt_dlp_opts()}
    with yt_dlp.YoutubeDL(opts) as ytdl:
        assert isinstance(ytdl, yt_dlp.YoutubeDL)
        response = await asyncio.to_thread(
            ytdl.extract_info, f"ytsearch{limit}:{text}", download=False
        )

    keyboard = [
        [
            InlineKeyboardButton(
                f"{video['channel']} {consts.SEP} {video['title']}",
                callback_data=f"{consts.SEARCH_CALLBACK} {video['id']}",
            )
        ]
        for video in response["entries"]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text("Выберите трек", reply_markup=reply_markup)
