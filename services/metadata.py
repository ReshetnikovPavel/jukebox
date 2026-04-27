import logging
import typing
from typing import Any

import music_tag
import requests
import ytmusicapi
from requests.models import Response
from ytmusicapi.models import Lyrics

import consts

WatchPlaylist = dict[str, list[dict[str, Any]] | str | None]
YtTrack = dict[str, Any]


def write_metadata(video_id: str, filepath: str) -> None:
    ytmusic = ytmusicapi.YTMusic(consts.YT_MUSIC_HEADERS_PATH)
    watch_playlist: WatchPlaylist = ytmusic.get_watch_playlist(video_id, limit=1)

    yt_meta = typing.cast(list[YtTrack], watch_playlist["tracks"])[0]

    lyrics = __get_lyrics(ytmusic, watch_playlist)
    artwork = __get_artwork(yt_meta)
    track_number = __get_track_number(ytmusic, yt_meta)

    tag_editor = music_tag.load_file(filepath)
    tag_editor["tracktitle"] = yt_meta["title"]
    tag_editor["artist"] = yt_meta["artists"][0]["name"]
    tag_editor["album"] = yt_meta["album"]["name"]
    tag_editor["year"] = yt_meta["year"]
    if track_number is not None:
        tag_editor["tracknumber"] = track_number
    if lyrics is not None:
        tag_editor["lyrics"] = lyrics
    if artwork is not None:
        tag_editor["artwork"] = artwork
    tag_editor.save()


def __get_lyrics(
    ytmusic: ytmusicapi.YTMusic,
    watch_playlist: WatchPlaylist,
) -> str | None:
    lyrics_id = watch_playlist["lyrics"]
    if lyrics_id is None:
        return None
    assert isinstance(lyrics_id, str)

    lyrics = ytmusic.get_lyrics(lyrics_id, timestamps=False)
    if lyrics is None:
        return None
    return lyrics["lyrics"]


def __get_artwork(yt_meta: YtTrack) -> bytes | None:
    thumbnails = yt_meta["thumbnail"]
    widest_thumbnail = max(thumbnails, key=lambda t: t["width"], default=None)
    if widest_thumbnail is None:
        return None

    url = widest_thumbnail["url"]
    image_response = typing.cast(Response, requests.get(url))
    if not image_response.ok:
        logging.error("Unable to get artwork", image_response)
        return None

    return image_response.content


def __get_track_number(ytmusic: ytmusicapi.YTMusic, yt_meta: YtTrack) -> int | None:
    album_id = yt_meta["album"]["id"]
    album = ytmusic.get_album(album_id)

    track_from_album = None
    for track in album["tracks"]:
        if track["title"] == yt_meta["title"]:
            track_from_album = track
            break

    if track_from_album is None:
        logging.error("Track not found in the album", album)
        return None

    track_number = track_from_album["trackNumber"]
    return track_number
