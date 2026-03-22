from dataclasses import dataclass
from types import GeneratorType

from telegram import CallbackQuery, Message, Update
from telegram.ext import ContextTypes

import services


async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    assert chat is not None

    callback_query = update.callback_query
    assert callback_query is not None

    download_album_message = await context.bot.send_message(
        chat.id, "Загружаю все треки из альбома"
    )

    for song in get_songs(callback_query):
        await services.download_and_send_song(
            song.video_id, song.artists_title_str, update, context
        )
    await download_album_message.delete()


@dataclass()
class Song:
    video_id: str
    artists_title_str: str


def get_songs(callback_query: CallbackQuery) -> GeneratorType[Song]:
    message = callback_query.message
    assert message is not None
    assert isinstance(message, Message)

    reply_markup = message.reply_markup
    assert reply_markup is not None

    for line in reply_markup.inline_keyboard:
        button = line[0]
        data = button.callback_data
        assert isinstance(data, str)

        parts = data.split(maxsplit=1)
        if len(parts) == 2:
            yield Song(video_id=parts[1], artists_title_str=button.text)
