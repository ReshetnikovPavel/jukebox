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


async def singles_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    singles = artist["singles"]["results"]
    if params := artist["singles"].get("params"):
        singles = await asyncio.to_thread(
            ytmusic.get_artist_albums, artist["singles"]["browseId"], params
        )

    if len(singles) == 0:
        await context.bot.send_message(chat.id, "Ничего не нашлось 😭")
        return

    reply_markup = services.paging.make_paging_keyboard(
        singles,
        "browseId",
        from_id,
        LIMIT,
        lambda single: InlineKeyboardButton(
            f"{artist['name']} {consts.SEP} {single['title']}",
            callback_data=f"{consts.ALBUM_GET} {single['browseId']}",
        ),
        lambda from_id: InlineKeyboardButton(
            "←",
            callback_data=f"{consts.ARTIST_SINGLES} {artist_id} {from_id} {consts.REPLACE_MESSAGE}",
        ),
        lambda from_id: InlineKeyboardButton(
            "→",
            callback_data=f"{consts.ARTIST_SINGLES} {artist_id} {from_id} {consts.REPLACE_MESSAGE}",
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
            chat.id, "Выберите сингл", reply_markup=reply_markup
        )
