import asyncio

from telegram import InlineKeyboardButton, Update
from telegram.error import TelegramError, TimedOut
from telegram.ext import ContextTypes

import consts
import services
import services.paging
from handlers.error import report
from services.yt_cache import CachedYTMusic as YTMusic

LIMIT = 10


async def songs_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    assert chat is not None

    callback_query = update.callback_query
    assert callback_query is not None

    callback_data = callback_query.data
    assert callback_data is not None

    message = callback_query.message
    assert message is not None

    parts = callback_data.split()
    artist_id = parts[1]
    from_id = parts[2] if len(parts) > 2 else None
    replace = parts[3] if len(parts) > 3 else None

    ytmusic = YTMusic(consts.YT_MUSIC_HEADERS_PATH)
    artist = await asyncio.to_thread(ytmusic.get_artist, artist_id)

    songs_browse_id = artist["songs"]["browseId"]
    playlist = await asyncio.to_thread(
        ytmusic.get_playlist, songs_browse_id, limit=None
    )

    tracks = playlist["tracks"]

    if len(tracks) == 0:
        await context.bot.send_message(chat.id, "Ничего не нашлось 😭")
        return

    reply_markup = services.paging.make_paging_keyboard(
        tracks,
        "videoId",
        from_id,
        LIMIT,
        lambda t: InlineKeyboardButton(
            f"{', '.join(a['name'] for a in t['artists'])} {consts.SEP} {t['title']}",
            callback_data=f"{consts.SONG_DOWNLOAD} {t['videoId']} {t['album']['id']}",
        ),
        lambda from_id: InlineKeyboardButton(
            "←",
            callback_data=f"{consts.ARTIST_SONGS} {artist_id} {from_id} {consts.REPLACE_MESSAGE}",
        ),
        lambda from_id: InlineKeyboardButton(
            "→",
            callback_data=f"{consts.ARTIST_SONGS} {artist_id} {from_id} {consts.REPLACE_MESSAGE}",
        ),
    )

    if replace:
        try:
            await context.bot.edit_message_reply_markup(
                chat.id, message.message_id, reply_markup=reply_markup
            )
        except TelegramError as e:
            await report(e, update, context, "WARN: Скорее всего дважды нажали")
        except TimedOut as e:
            await report(e, update, context, "WARN: Скорее всего дважды нажали")
    else:
        await context.bot.send_message(
            chat.id, "Выберите трек", reply_markup=reply_markup
        )
