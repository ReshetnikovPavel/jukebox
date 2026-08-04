from urllib.parse import parse_qs, urlparse

import validators
from telegram import Update
from telegram.ext import ContextTypes

import services


async def download_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    assert chat is not None

    message = update.message or update.edited_message
    assert message is not None

    link = message.text
    assert link is not None
    assert validators.url(link)

    parsed_url = urlparse(link)
    domain = parsed_url.netloc
    match domain:
        case "music.youtube.com":
            video_id = parse_qs(parsed_url.query)["v"][0]
            await services.download_and_send_track(video_id, update, context, chat.id)
        case "www.youtube.com" | "youtube.com":
            video_id = parse_qs(parsed_url.query)["v"][0]
            await services.download_and_send_track(
                video_id, update, context, chat.id, parse_video_title=True
            )
        case "www.youtu.be" | "youtu.be":
            video_id = parsed_url.path.split("/")[1]
            await services.download_and_send_track(
                video_id, update, context, chat.id, parse_video_title=True
            )
        case _:
            await services.download_and_send_audio_from_video(link, context, chat.id)
