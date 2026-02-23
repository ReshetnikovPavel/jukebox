import telegram
import consts


def default_yt_dlp_opts() -> dict:
    return {
        "cookiefile": consts.YT_COOKIES_PATH,
        "js_runtimes": {"node": {}},
    }


def chunks(s: str, chunk_len: int) -> list[str]:
    assert chunk_len >= 0
    return [s[i : i + chunk_len] for i in range(0, len(s), chunk_len)]


async def send_long_message(bot: telegram.Bot, chat_id: int | str, text: str) -> None:
    for chunk in chunks(text, 4096):
        await bot.send_message(chat_id, chunk)
