import asyncio
import os
import sqlite3


def _get_db_path() -> str:
    return os.environ.get("SQLITE_PATH", "jukebox.db")


CREATE_TABLE_TRACKS = """
    CREATE TABLE IF NOT EXISTS tracks (
        id INTEGER NOT NULL PRIMARY KEY,
        video_id TEXT NOT NULL,
        browse_id TEXT,
        file_id TEXT NOT NULL,
        UNIQUE(video_id, browse_id)
    );
"""

CREATE_TRACKS_INDICES = """
    CREATE INDEX IF NOT EXISTS idx_video_id ON tracks(video_id);
"""


def init_db() -> None:
    with sqlite3.connect(_get_db_path()) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute(CREATE_TABLE_TRACKS)
        conn.execute(CREATE_TRACKS_INDICES)


ADD_TRACK = """
    INSERT INTO tracks (video_id, browse_id, file_id)
    VALUES (?, ?, ?)
    ON CONFLICT(video_id, browse_id) DO UPDATE SET
        file_id = excluded.file_id;
"""


async def add_track(video_id: str, browse_id: str | None, file_id: str) -> None:
    def func():
        with sqlite3.connect(_get_db_path()) as conn:
            conn.execute(ADD_TRACK, (video_id, browse_id, file_id))
            conn.commit()
    return await asyncio.to_thread(func)


GET_FILE_ID_FROM_VIDEO_ID_AND_BROWSE_ID = """
    SELECT file_id FROM tracks
    WHERE video_id = ? AND browse_id = ?
"""

GET_FILE_ID_FROM_VIDEO_ID = """
    SELECT file_id FROM tracks
    WHERE video_id = ? AND browse_id IS NULL
"""


async def get_file_id(video_id: str, browse_id: str | None) -> str | None:
    def func():
        with sqlite3.connect(_get_db_path()) as conn:
            cur = conn.cursor()
            if browse_id is None:
                cur.execute(GET_FILE_ID_FROM_VIDEO_ID, (video_id,))
            else:
                cur.execute(GET_FILE_ID_FROM_VIDEO_ID_AND_BROWSE_ID, (video_id, browse_id))
            row = cur.fetchone()
            return row[0] if row else None
    return await asyncio.to_thread(func)
