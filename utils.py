from typing import Any
import telegram
from telegram import CallbackQuery, Message

import consts


def default_yt_dlp_opts() -> dict:
    return {
        "cookiefile": consts.YT_COOKIES_PATH,
        "js_runtimes": {"node": {}},
    }


def split_command(s: str) -> tuple[str | None, str]:
    if s.startswith("/"):
        splits = s.split(maxsplit=1)
        if len(splits) == 1:
            return (splits[0].strip(), "")
        else:
            return (splits[0].strip(), splits[1].strip())
    return (None, s.strip())


def chunks(s: str, chunk_len: int) -> list[str]:
    assert chunk_len >= 0
    return [s[i : i + chunk_len] for i in range(0, len(s), chunk_len)]


async def send_long_message(
    bot: telegram.Bot, chat_id: int | str, text: str, **kwargs
) -> None:
    for chunk in chunks(text, 4096):
        await bot.send_message(chat_id, chunk, **kwargs)


def get_selected_button_text(callback_query: CallbackQuery, id: str) -> str | None:
    message = callback_query.message
    assert message is not None
    assert isinstance(message, Message)

    reply_markup = message.reply_markup
    assert reply_markup is not None

    for line in reply_markup.inline_keyboard:
        button = line[0]
        data = button.callback_data
        assert isinstance(data, str)

        if data.find(id) != -1:
            return button.text


def get_performer_and_title_from_reply(message: Message) -> tuple[str, str] | None:
    reply = message.reply_to_message
    if reply is None:
        return None
    audio = reply.audio
    if audio is None:
        return None
    title = audio.title
    if title is None:
        return None
    performer = audio.performer
    if performer is None:
        return None
    return performer, title


def get_song_from_search_response(
    tracks: list[dict[str, Any]],
    artist: str,
    title: str,
) -> dict[str, Any] | None:
    artists = set(artist.split(", "))
    for track in tracks:
        track_artists = {a["name"] for a in track["artists"]}
        if track["title"] == title and track_artists == artists:
            return track
