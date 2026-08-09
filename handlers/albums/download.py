from dataclasses import dataclass
from types import GeneratorType

from telegram import CallbackQuery, Message, Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

import consts
import handlers.songs
import services
from services import cache
from services.metadata import TrackMetadata


async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    assert chat is not None

    callback_query = update.callback_query
    assert callback_query is not None

    callback_data = callback_query.data
    assert callback_data is not None

    browse_id = callback_data.split(maxsplit=1)[1]

    songs = list(get_songs(callback_query))
    file_ids_in_cache = [
        await cache.get_file_id(song.video_id, browse_id) for song in songs
    ]
    if all(file_ids_in_cache):
        for file_id in file_ids_in_cache:
            assert file_id is not None
            await context.bot.send_audio(chat.id, file_id)
            continue
        return

    download_album_message = await context.bot.send_message(
        chat.id, "Загружаю все треки из альбома"
    )

    metadata_message = await context.bot.send_message(chat.id, "Загружаю метадату")
    meta_by_title: dict[str, TrackMetadata] = {}
    try:
        meta_by_title = {
            s.title: s for s in await services.get_metadata_by_browse_id(browse_id)
        }
    except Exception as e:
        await context.bot.send_message(chat.id, "Не получилось найти метадату 😭")
        await handlers.error.report(
            e, update, context, "WARN: Unable to get metadata, skipping"
        )
    await metadata_message.delete()

    for song, file_id in zip(songs, file_ids_in_cache):
        if file_id:
            await context.bot.send_audio(chat.id, file_id)
            continue

        async with services.download_track(
            song.video_id, song.artist, song.title, update, context
        ) as audio_path:
            try:
                if meta_by_title:
                    track_meta = meta_by_title[song.title]
                else:
                    track_meta = await services.get_metadata(song.video_id, browse_id)
                services.write_metadata(track_meta, audio_path)
                has_written_metadata = True
            except Exception as e:
                await context.bot.send_message(
                    chat.id, "Трек загрузился, но не получилось записать метадату 😭"
                )
                await handlers.error.report(
                    e, update, context, "WARN: Unable to write metadata, skipping"
                )
                has_written_metadata = False

            try:
                res = await context.bot.send_audio(
                    chat.id,
                    audio_path,
                    title=song.title,
                    performer=song.artist,
                    write_timeout=6400,
                )
                assert res.audio is not None
                if has_written_metadata:
                    await cache.add_track(song.video_id, browse_id, res.audio.file_id)
            except TelegramError as e:
                await handlers.error.report(
                    e,
                    update,
                    context,
                    "WARN: stopped waiting for telegram respond to audio upload",
                )

    await download_album_message.delete()


@dataclass()
class Song:
    video_id: str
    artist: str
    title: str


def get_songs(callback_query: CallbackQuery) -> GeneratorType[Song]:
    message = callback_query.message
    assert message is not None
    assert isinstance(message, Message)

    reply_markup = message.reply_markup
    assert reply_markup is not None

    for line in reply_markup.inline_keyboard:
        button = line[0]
        if consts.SEP not in button.text:
            continue
        data = button.callback_data
        assert isinstance(data, str)

        artist, title = button.text.split(consts.SEP, maxsplit=1)
        artist = artist.strip()
        title = title.strip()

        parts = data.split(maxsplit=1)
        yield Song(video_id=parts[1], artist=artist, title=title)


def get_browse_id(callback_query: CallbackQuery) -> str | None:
    message = callback_query.message
    assert message is not None
    assert isinstance(message, Message)

    reply_markup = message.reply_markup
    assert reply_markup is not None

    for line in reply_markup.inline_keyboard:
        button = line[0]
        if consts.SEP in button.text:
            continue
        data = button.callback_data
        assert isinstance(data, str)

        parts = data.split(maxsplit=1)
        return parts[1]
    return None
