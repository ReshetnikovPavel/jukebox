import asyncio
from dataclasses import dataclass

import music_tag
import ytmusicapi

import consts
import services


@dataclass
class TrackMetadata:
    is_video: bool
    title: str
    artist: str
    album: str | None
    album_artist: str | None
    year: str | None
    track_number: int | None
    lyrics: str | None
    artwork: bytes | None
    total_tracks: int | None


def write_metadata(metadata: TrackMetadata, filepath: str) -> None:
    tag_editor = music_tag.load_file(filepath)
    tag_editor["tracktitle"] = metadata.title
    tag_editor["artist"] = metadata.artist
    if metadata.album_artist is not None:
        tag_editor["albumartist"] = metadata.album_artist
    if metadata.album is not None:
        tag_editor["album"] = metadata.album
    if metadata.year is not None:
        tag_editor["year"] = metadata.year
    if metadata.total_tracks is not None:
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
    if "album" not in track:
        artwork = await services.get_widest_thumbnail(track["thumbnail"])
        metadata = __get_metadata_for_video(track, artwork)
        return metadata

    album_browse_id = album_browse_id or track["album"]["id"]

    album = await asyncio.to_thread(ytmusic.get_album, album_browse_id)
    artwork = await services.get_widest_thumbnail(album["thumbnails"])
    lyrics = await services.get_lyrics_from_playlist(ytmusic, watch_playlist)
    for track in album["tracks"]:
        if track["title"] == title:
            break
    metadata = __get_metadata_for_song(album, track, artwork, lyrics)
    return metadata


async def get_metadata_by_album_browse_id(browse_id: str) -> list[TrackMetadata]:
    ytmusic = YTMusic(consts.YT_MUSIC_HEADERS_PATH)
    album = await asyncio.to_thread(ytmusic.get_album, browse_id)
    artwork = await services.get_widest_thumbnail(album["thumbnails"])

    metadatas: list[TrackMetadata] = []
    for track in album["tracks"]:
        lyrics = await services.get_lyrics_from_video_id(ytmusic, track["videoId"])
        metadata = __get_metadata_for_song(album, track, artwork, lyrics)
        metadatas.append(metadata)
    return metadatas


def __get_metadata_for_video(track: dict, artwork: bytes | None) -> TrackMetadata:
    title = track["title"]
    artist = ", ".join(a["name"] for a in track["artists"])
    return TrackMetadata(
        is_video=True,
        title=title,
        artist=artist,
        artwork=artwork,
        album=None,
        album_artist=None,
        year=None,
        track_number=None,
        lyrics=None,
        total_tracks=None,
    )


def __get_metadata_for_song(
    album: dict,
    track: dict,
    artwork: bytes | None,
    lyrics: str | None,
) -> TrackMetadata:
    album_artist = ", ".join(a["name"] for a in album["artists"])
    album_title = album["title"]
    year = album["year"]
    total_tracks = album["trackCount"]

    title = track["title"]
    artist = ", ".join(a["name"] for a in track["artists"])
    track_number = track["trackNumber"]

    return TrackMetadata(
        is_video=False,
        title=title,
        artist=artist,
        album=album_title,
        album_artist=album_artist,
        year=year,
        track_number=track_number,
        lyrics=lyrics,
        artwork=artwork,
        total_tracks=total_tracks,
    )
