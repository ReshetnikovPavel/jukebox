import logging
import asyncio
import typing
from dataclasses import dataclass
from typing import Any

import music_tag
import requests
import ytmusicapi
from requests.models import Response

import consts
import services


@dataclass
class TrackMetadata:
    title: str
    artist: str
    album: str
    album_artist: str
    year: str
    track_number: int | None
    lyrics: str | None
    artwork: bytes | None
    total_tracks: int
    video_id: str


def write_metadata(metadata: TrackMetadata, filepath: str) -> None:
    tag_editor = music_tag.load_file(filepath)
    tag_editor["tracktitle"] = metadata.title
    tag_editor["artist"] = metadata.artist
    tag_editor["albumartist"] = metadata.album_artist
    tag_editor["album"] = metadata.album
    tag_editor["year"] = metadata.year
    tag_editor["totaltracks"] = metadata.total_tracks
    if metadata.track_number is not None:
        tag_editor["tracknumber"] = metadata.track_number
    if metadata.lyrics is not None:
        tag_editor["lyrics"] = metadata.lyrics
    if metadata.artwork is not None:
        tag_editor["artwork"] = metadata.artwork
    tag_editor.save()


async def get_metadata_by_video_id(
    video_id: str, album_browse_id: str | None = None
) -> TrackMetadata:
    ytmusic = ytmusicapi.YTMusic(consts.YT_MUSIC_HEADERS_PATH)
    watch_playlist = await asyncio.to_thread(
        ytmusic.get_watch_playlist, video_id, limit=1
    )

    tracks = watch_playlist["tracks"]
    assert isinstance(tracks, list)
    track = tracks[0]
    title = track["title"]
    album_browse_id = album_browse_id or track["album"]["id"]

    album = await asyncio.to_thread(ytmusic.get_album, album_browse_id)
    artwork = await __get_artwork(album["thumbnails"])
    lyrics = await services.get_lyrics(ytmusic, watch_playlist)
    for track in album["tracks"]:
        if track["title"] == title:
            break
    metadata = __get_metadata(album, track, artwork, lyrics)
    return metadata


async def get_metadata_by_album_browse_id(browse_id: str) -> list[TrackMetadata]:
    ytmusic = ytmusicapi.YTMusic(consts.YT_MUSIC_HEADERS_PATH)
    album = await asyncio.to_thread(ytmusic.get_album, browse_id)
    artwork = await __get_artwork(album["thumbnails"])

    metadatas: list[TrackMetadata] = []
    for track in album["tracks"]:
        watch_playlist = await asyncio.to_thread(
            ytmusic.get_watch_playlist, track["videoId"], limit=1
        )
        lyrics = await services.get_lyrics(ytmusic, watch_playlist)
        metadata = __get_metadata(album, track, artwork, lyrics)
        metadatas.append(metadata)
    return metadatas


def __get_metadata(
    album: dict,
    track: dict,
    artwork: bytes | None,
    lyrics: str | None,
) -> TrackMetadata:
    logging.info(f"ALBUM::: {album}")
    logging.info(f"TRACK::: {track}")
    album_artist = ", ".join(a["name"] for a in album["artists"])
    album_title = album["title"]
    year = album["year"]
    total_tracks = album["trackCount"]

    title = track["title"]
    artist = ", ".join(a["name"] for a in track["artists"])
    track_number = track["trackNumber"]
    video_id = track["videoId"]

    return TrackMetadata(
        title=title,
        artist=artist,
        album=album_title,
        album_artist=album_artist,
        year=year,
        track_number=track_number,
        lyrics=lyrics,
        artwork=artwork,
        total_tracks=total_tracks,
        video_id=video_id,
    )


async def __get_artwork(thumbnails: list[dict[str, Any]]) -> bytes | None:
    widest_thumbnail = max(thumbnails, key=lambda t: t["width"], default=None)
    if widest_thumbnail is None:
        return None

    url = widest_thumbnail["url"]
    image_response = await asyncio.to_thread(requests.get, url)
    image_response = typing.cast(Response, image_response)
    if not image_response.ok:
        raise Exception("Unable to get artwork", image_response)

    return image_response.content
