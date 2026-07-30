import asyncio
import os
import sqlite3


def _get_db_path() -> str:
    return os.environ.get("SQLITE_PATH", "jukebox.db")


CREATE_TABLE_TRACKS = """
    CREATE TABLE IF NOT EXISTS tracks (
        video_id TEXT PRIMARY KEY,
        file_id TEXT NOT NULL
    )
"""


def init_db() -> None:
    with sqlite3.connect(_get_db_path()) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute(CREATE_TABLE_TRACKS)


ADD_TRACK = """
    INSERT INTO tracks (video_id, file_id)
    VALUES (?, ?)
    ON CONFLICT(video_id) DO UPDATE SET file_id = excluded.file_id;
"""


async def add_track(video_id: str, file_id: str) -> None:
    def func():
        with sqlite3.connect(_get_db_path()) as conn:
            conn.execute(ADD_TRACK, (video_id, file_id))
            conn.commit()
    return await asyncio.to_thread(func)


GET_FILE_ID = """
    SELECT file_id FROM tracks
    WHERE video_id = ?
"""


async def get_file_id(video_id: str) -> str | None:
    def func():
        with sqlite3.connect(_get_db_path()) as conn:
            cur = conn.cursor()
            cur.execute(GET_FILE_ID, (video_id,))
            row = cur.fetchone()
            return row[0] if row else None
    return await asyncio.to_thread(func)
