import logging
import os
import sqlite3

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


def _get_db_path() -> str:
    return os.environ.get("SQLITE_PATH", "jukebox.db")


async def migrate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with sqlite3.connect(_get_db_path()) as conn:
        conn.execute("DROP TABLE tracks")
        logger.info("DELETED TABLE tracks")
        conn.execute("ALTER TABLE tracks_tmp RENAME TO tracks")
        logger.info("RENAMED TABLE tracks_tmp to tracks")
