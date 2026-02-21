import consts


def default_yt_dlp_opts() -> dict:
    return {
        "cookiefile": consts.YT_COOKIES_PATH,
        "js_runtimes": {"node": {}},
    }
