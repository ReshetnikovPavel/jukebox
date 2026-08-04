import asyncio

import ytmusicapi
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

import consts

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
    from_id = parts[2]
    replace = parts[3] if len(parts) > 3 else None

    ytmusic = ytmusicapi.YTMusic(consts.YT_MUSIC_HEADERS_PATH)
    artist = await asyncio.to_thread(ytmusic.get_artist, artist_id)

    songs_browse_id = artist["songs"]["browseId"]
    playlist = await asyncio.to_thread(
        ytmusic.get_playlist, songs_browse_id, limit=None
    )

    tracks = playlist["tracks"]

    from_index = None
    for i, track in enumerate(tracks):
        if track["videoId"] == from_id:
            from_index = i
            break
    assert from_index is not None

    if len(tracks) == 0:
        await context.bot.send_message(chat.id, "Ничего не нашлось 😭")
        return

    keyboard = [
        [
            InlineKeyboardButton(
                f"{', '.join(a['name'] for a in t['artists'])} {consts.SEP} {t['title']}",
                callback_data=f"{consts.SONG_DOWNLOAD} {t['videoId']}",
            )
        ]
        for t in tracks[from_index : from_index + LIMIT]
    ]

    paging_row = []
    if tracks[0]["videoId"] != from_id:
        prev_from_track = (
            tracks[from_index - LIMIT] if from_index > LIMIT else tracks[0]
        )
        prev_from_id = prev_from_track["videoId"]
        paging_row.append(
            InlineKeyboardButton(
                "←",
                callback_data=f"{consts.ARTIST_SONGS} {artist_id} {prev_from_id} {consts.REPLACE_MESSAGE}",
            )
        )
    if from_index + LIMIT < len(tracks):
        next_from_id = tracks[from_index + LIMIT]["videoId"]
        paging_row.append(
            InlineKeyboardButton(
                "→",
                callback_data=f"{consts.ARTIST_SONGS} {artist_id} {next_from_id} {consts.REPLACE_MESSAGE}",
            )
        )
    keyboard.append(paging_row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    if replace:
        await context.bot.edit_message_reply_markup(
            chat.id, message.message_id, reply_markup=reply_markup
        )
    else:
        await context.bot.send_message(
            chat.id, "Выберите трек", reply_markup=reply_markup
        )
