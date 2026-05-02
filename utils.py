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
            return (splits[0], "")
        else:
            return (splits[0], splits[1])
    return (None, s)


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
