from dataclasses import dataclass


@dataclass()
class Track:
    title: str
    artists: list[str]
    video_id: str


def into_track(data: dict) -> Track:
    title = data["title"]
    artists = [artist["name"] for artist in data["artists"]]
    video_id = data["videoId"]
    return Track(title, artists, video_id)
