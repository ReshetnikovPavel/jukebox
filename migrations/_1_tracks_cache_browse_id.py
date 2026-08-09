import asyncio
import logging
import os
import sqlite3
import tempfile
from typing import Any

import music_tag
from telegram import Update
from telegram.ext import ContextTypes
from ytmusicapi import YTMusic

import consts


def _get_db_path() -> str:
    return os.environ.get("SQLITE_PATH", "jukebox.db")


async def search_browse_id(
    ytmusic: YTMusic, video_id: str, title: str, artist: str, album_name: str
) -> dict[str, Any] | None:
    artists = set(artist.split(", "))
    query = f"{artist} {album_name}"
    albums = await asyncio.to_thread(ytmusic.search, query, filter="albums")
    logging.info(
        f"FOUND ALBUMS: {[(', '.join(artist['name'] for artist in a['artists']), a['title']) for a in albums]}"
    )
    for album in albums:
        if album["title"] == album_name and ({artist['name'] for artist in album['artists'] } & artists):
            return album["browseId"]

    query = f"{artist} {title}"
    tracks = await asyncio.to_thread(ytmusic.search, query, filter="songs")
    logging.info(
        f"FOUND TRACKS: {[(t["videoId"], ', '.join(a['name'] for a in t['artists']), t['title'], t['album']['name'] if t.get('album') else None) for t in tracks]}"
    )
    for track in tracks:
        if track["videoId"] == video_id and track["album"]["name"] == album_name:
            return track["album"]["id"]
    return None


async def migrate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with sqlite3.connect(_get_db_path()) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tracks_tmp (
                id INTEGER NOT NULL PRIMARY KEY,
                video_id TEXT NOT NULL,
                browse_id TEXT,
                file_id TEXT NOT NULL,
                UNIQUE(video_id, browse_id)
            );""")
        logging.info(f"CREATED TABLE tracks_tmp")
        cur = conn.cursor()
        for video_id, file_id in cur.execute("SELECT video_id, file_id FROM tracks"):
            cur_inner = conn.cursor()
            cur_inner.execute(
                """
                SELECT video_id FROM tracks_tmp
                WHERE video_id = ?
            """,
                (video_id,),
            )
            if cur_inner.fetchone():
                logging.info(f"SKIPPING, Already saved `{video_id}` `{file_id}`")
                continue

            logging.info(f"UPDATING `{video_id}` `{file_id}`")
            file = await context.bot.get_file(file_id)

            with tempfile.TemporaryDirectory() as tmp_dir:
                path = await file.download_to_drive(os.path.join(tmp_dir, "file.mp3"))
                tag_editor = music_tag.load_file(path)
                title = tag_editor["tracktitle"].first
                artist = tag_editor["artist"].first
                album = tag_editor["album"].first
                logging.info(f"TRACK `{title}` `{artist}` `{album}`")

                ytmusic = YTMusic(consts.YT_MUSIC_HEADERS_PATH)
                browse_id = await search_browse_id(
                    ytmusic, video_id, title, artist, album
                )
                if browse_id is None:
                    logging.warning(
                        f"TRACK NOT FOUND `{video_id}` `{title}` `{artist}` `{album}`"
                    )
                else:
                    logging.info(f"BROWSE_ID `{video_id}` `{browse_id}` `{file_id}`")

                conn.execute(
                    """
                    INSERT INTO tracks_tmp (video_id, browse_id, file_id)
                    VALUES (?, ?, ?)
                     ON CONFLICT(video_id, browse_id) DO UPDATE SET
                         file_id = excluded.file_id;
                 """,
                    (video_id, browse_id, file_id),
                )
            logging.info(f"UPDATED `{video_id}` `{browse_id}` `{file_id}`")
            conn.commit()

        # conn.execute("DROP TABLE tracks")
        # logging.info(f"DELETED TABLE tracks")
        # conn.execute("ALTER TABLE tracks_tmp RENAME TO tracks")
        # logging.info(f"RENAMED TABLE tracks_tmp to tracks")
