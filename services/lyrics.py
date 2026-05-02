import asyncio
import typing

import ytmusicapi
from ytmusicapi.models import Lyrics


async def get_lyrics(ytmusic: ytmusicapi.YTMusic, watch_playlist: dict) -> str | None:
    lyrics_id = watch_playlist["lyrics"]
    if lyrics_id is None:
        return None
    assert isinstance(lyrics_id, str)

    lyrics = await asyncio.to_thread(ytmusic.get_lyrics, lyrics_id, timestamps=False)
    if lyrics is None:
        return None
    lyrics = typing.cast(Lyrics, lyrics)["lyrics"]
    return lyrics
