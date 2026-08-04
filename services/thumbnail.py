import asyncio
import typing
from typing import Any

import requests
from requests.models import Response


async def get_widest_thumbnail(thumbnails: list[dict[str, Any]]) -> bytes | None:
    widest_thumbnail = max(thumbnails, key=lambda t: t["width"], default=None)
    if widest_thumbnail is None:
        return None

    url = widest_thumbnail["url"]
    image_response = await asyncio.to_thread(requests.get, url)
    image_response = typing.cast(Response, image_response)
    if not image_response.ok:
        raise Exception("Unable to get artwork", image_response)

    return image_response.content
