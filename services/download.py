import asyncio
import json
import os
import subprocess
import tempfile
from contextlib import asynccontextmanager
from types import AsyncGeneratorType

import youtube_title_parse
import yt_dlp
from telegram import Update
from telegram.ext import ContextTypes
from yt_dlp.utils import DownloadError

import consts
import handlers
import services
import utils
from services import cache
from services.metadata import TrackMetadata


async def download_and_send_track(
    video_id: str,
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    browse_id: str | None = None,
    artist: str | None = None,
    title: str | None = None,
    parse_video_title: bool = False,
) -> None:
    if file_id := await cache.get_file_id(video_id):
        await context.bot.send_audio(chat_id, file_id)
        return

    try:
        metadata = await services.get_metadata_by_video_id(video_id, browse_id)
    except Exception as e:
        await context.bot.send_message(chat_id, "Не получилось найти метадату 😭")
        await handlers.error.report(e, update, context, "WARN: Unable to get metadata, skipping")
        metadata = None

    (artist, title) = __get_artist_title(metadata, title, artist, parse_video_title)
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
            await handlers.error.report(e, update, context, "WARN: Unable to write metadata, skipping")

        res = await context.bot.send_audio(
            chat_id, audio_path, title=title, performer=artist, write_timeout=3600
        )
        assert res.audio is not None
        if metadata is not None:
            await cache.add_track(video_id, res.audio.file_id)


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


DOWNLOAD_SEMAPHORE = asyncio.Semaphore(2)


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

        async with DOWNLOAD_SEMAPHORE:
            try:
                with yt_dlp.YoutubeDL(opts) as ytdl:
                    await asyncio.to_thread(ytdl.download, link)
            except DownloadError as e:
                await handlers.error.report(e, update, context, f"WARN: unable to download track {filename_without_ext}, trying again with cookies")
                opts["cookiefile"] = consts.YT_COOKIES_PATH
                with yt_dlp.YoutubeDL(opts) as ytdl:
                    await asyncio.to_thread(ytdl.download, link)

        mp3_path = os.path.join(tmp_dir, f"{filename_without_ext}.mp3")
        await asyncio.to_thread(
            subprocess.check_call, ["ffmpeg", "-i", webm_path, mp3_path]
        )

        try:
            yield mp3_path
        finally:
            await download_message.delete()


async def download_and_send_audio_from_video(
    link: str,
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
) -> None:
    download_message = await context.bot.send_message(
        chat_id, "Скачиваю аудио из видео"
    )

    with tempfile.TemporaryDirectory() as tmp_dir:
        out_path = os.path.join(tmp_dir, "audio.mp3")
        opts = {
            "extract_audio": True,
            "writeinfojson": True,
            "noplaylist": True,
            "format": "bestaudio",
            "outtmpl": out_path,
            **utils.default_yt_dlp_opts(),
        }

        async with DOWNLOAD_SEMAPHORE:
            with yt_dlp.YoutubeDL(opts) as ytdl:
                await asyncio.to_thread(ytdl.download, link)

        with open(out_path + ".info.json") as metadata_file:
            metadata = json.load(metadata_file)
            title = metadata["title"]
            performer = metadata["uploader"]

        await context.bot.send_audio(
            chat_id, out_path, title=title, performer=performer
        )

    await download_message.delete()
