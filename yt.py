import yt_dlp
import ytmusicapi

import consts


def get_ytmusicapi() -> ytmusicapi.YTMusic:
    return ytmusicapi.YTMusic(consts.YT_MUSIC_HEADERS_PATH)


def get_yt_dlp(out_path: str) -> yt_dlp.YoutubeDL:
    return yt_dlp.YoutubeDL(
        {
            "extract_audio": True,
            "format": "bestaudio",
            "outtmpl": out_path,
        }
    )
