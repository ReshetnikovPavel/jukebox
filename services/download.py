from services.metadata import TrackMetadata
import typing
import asyncio
import os
import subprocess
import tempfile
from contextlib import asynccontextmanager
from types import AsyncGeneratorType

import youtube_title_parse
import yt_dlp
from telegram import Update
from telegram.ext import ContextTypes

import consts
import handlers
import services
import utils


async def download_and_send_track(
    video_id: str,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    browse_id: str | None = None,
    artist: str | None = None,
    title: str | None = None,
    parse_video_title: bool = False,
):
    try:
        metadata = await services.get_metadata_by_video_id(video_id, browse_id)
    except Exception as e:
        await context.bot.send_message(chat_id, "Не получилось найти метадату 😭")
        await handlers.error.report(e, update, context)
        metadata = None

    (artist, title) = __get_artist_title(metadata, artist, title, parse_video_title)
    if metadata is not None:
        metadata.artist = artist
        metadata.title = title

    assert title is not None
    assert artist is not None
    async with download_track(video_id, artist, title, update, context) as audio_path:
        try:
            if metadata is not None:
                services.write_metadata(metadata, audio_path)
        except Exception as e:
            await context.bot.send_message(
                chat_id, "Трек загрузился, но не получилось записать метадату 😭"
            )
            await handlers.error.report(e, update, context)

        await context.bot.send_audio(
            chat_id, audio_path, title=title, performer=artist, write_timeout=3600
        )


def __get_artist_title(
    metadata: TrackMetadata | None,
    title: str | None,
    artist: str | None,
    parse_video_title: bool,
) -> tuple[str, str]:
    if metadata is not None and not metadata.is_video:
        return (metadata.artist, metadata.title)

    if metadata is not None:
        artist = metadata.artist
        title = metadata.title

    if parse_video_title and (
        parse_result := youtube_title_parse.get_artist_title(title)
    ):
        return parse_result

    assert artist is not None
    assert title is not None
    return (artist, title)


@asynccontextmanager
async def download_track(
    video_id: str,
    artist: str,
    title: str,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> AsyncGeneratorType[str]:
    chat = update.effective_chat
    assert chat is not None

    download_message = await context.bot.send_message(
        chat.id, f"Загружаю трек {artist} {consts.SEP} {title}"
    )

    link = f"https://music.youtube.com/watch?v={video_id}"
    filename_without_ext = f"{artist} - {title}"
    with tempfile.TemporaryDirectory() as tmp_dir:
        webm_path = os.path.join(tmp_dir, f"{filename_without_ext}.webm")
        opts = {
            "extract_audio": True,
            "format": "bestaudio",
            "outtmpl": webm_path,
            **utils.default_yt_dlp_opts(),
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ytdl:
                await asyncio.to_thread(ytdl.download, link)
        except yt_dlp.DownloadError as e:
            await handlers.error.report(e, update, context)
            del opts["cookiefile"]
            with yt_dlp.YoutubeDL(opts) as ytdl:
                await asyncio.to_thread(ytdl.download, link)
        mp3_path = os.path.join(tmp_dir, f"{filename_without_ext}.mp3")
        subprocess.check_call(["ffmpeg", "-i", webm_path, mp3_path])

        try:
            yield mp3_path
        finally:
            await download_message.delete()
