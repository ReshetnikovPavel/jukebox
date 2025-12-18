import consts
from ytmusicapi import YTMusic, OAuthCredentials
import os


def get_ytmusicapi() -> YTMusic:
    client_id = os.environ.get(consts.YT_CLIENT_ID_VAR)
    if client_id is None:
        raise Exception(f"{consts.YT_CLIENT_ID_VAR} env variable is not present")

    client_secret = os.environ.get(consts.YT_CLIENT_SECRET_VAR)
    if client_secret is None:
        raise Exception(f"{consts.YT_CLIENT_SECRET_VAR} env variable is not present")

    return YTMusic(
        "browser.json",
        oauth_credentials=OAuthCredentials(
            client_id=client_id, client_secret=client_secret
        ),
    )
