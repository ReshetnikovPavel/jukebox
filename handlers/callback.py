import utils
from telegram import Update
from telegram.ext import ContextTypes

import consts
from handlers import albums, artists, lyrics, songs, video


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    callback_query = update.callback_query
    assert callback_query is not None

    callback_data = callback_query.data
    assert callback_data is not None

    await callback_query.answer()

    parts = callback_data.split()
    command = parts[0]
    match command:
        case consts.SONG_DOWNLOAD | consts.DEPRECATED_SEARCH_CALLBACK:
            return await songs.download_handler(update, context)
        case consts.LYRICS_GET | consts.DEPRECATED_SEARCH_CALLBACK_LYRICS:
            return await lyrics.get_handler(update, context)
        case consts.ALBUM_GET | consts.DEPRECATED_SEARCH_CALLBACK_ALBUMS:
            return await albums.get_handler(update, context)
        case consts.VIDEO_DOWNLOAD | consts.DEPRECATED_SEARCH_CALLBACK_VIDEO:
            return await video.download_handler(update, context)
        case consts.DEPRECATED_GET_CALLBACK_ALBUMS if consts.SEP in (
            utils.get_selected_button_text(callback_query, parts[1]) or ""
        ):
            return await songs.download_handler(update, context)
        case consts.ALBUM_DOWNLOAD | consts.DEPRECATED_GET_CALLBACK_ALBUMS:
            return await albums.download_handler(update, context)
        case consts.ARTIST_GET:
            return await artists.get_handler(update, context)
        case consts.ARTIST_ALBUMS:
            return await artists.albums_handler(update, context)
        case consts.ARTIST_SONGS:
            return await artists.songs_handler(update, context)
        case consts.ARTIST_SINGLES:
            return await artists.singles_handler(update, context)
        case _:
            raise Exception("Unknown callback_data", callback_data)
