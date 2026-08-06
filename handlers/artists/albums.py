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


async def albums_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    albums = artist["albums"]["results"]
    if params := artist["albums"].get("params"):
        albums = await asyncio.to_thread(
            ytmusic.get_artist_albums, artist["albums"]["browseId"], params
        )

    if len(albums) == 0:
        await context.bot.send_message(chat.id, "Ничего не нашлось 😭")
        return

    reply_markup = services.paging.make_paging_keyboard(
        albums,
        "browseId",
        from_id,
        LIMIT,
        lambda album: InlineKeyboardButton(
            f"{artist['name']} {consts.SEP} {album['title']}",
            callback_data=f"{consts.ALBUM_GET} {album['browseId']}",
        ),
        lambda from_id: InlineKeyboardButton(
            "←",
            callback_data=f"{consts.ARTIST_ALBUMS} {artist_id} {from_id} {consts.REPLACE_MESSAGE}",
        ),
        lambda from_id: InlineKeyboardButton(
            "→",
            callback_data=f"{consts.ARTIST_ALBUMS} {artist_id} {from_id} {consts.REPLACE_MESSAGE}",
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
            chat.id, "Выберите альбом", reply_markup=reply_markup
        )
