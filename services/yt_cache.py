import functools
import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any

from ytmusicapi import YTMusic


@dataclass
class CacheEntry:
    created_at: float
    accessed_at: float
    value: Any


_CACHE: dict[str, CacheEntry] = {}
_CACHE_TTL = 300
_CACHE_MAX_SIZE = 200


def cache_methods(methods: list[str]):
    def decorator(cls: type):
        for method_name in methods:
            original_method = getattr(cls, method_name)
            if not callable(original_method):
                continue

            @functools.wraps(original_method)
            def cached_method(
                self,
                *args,
                _method_name: str = method_name,
                _original_method: Any = original_method,
                **kwargs,
            ):
                key = _make_key(_method_name, args, kwargs)
                cached = _get_from_cache(key)
                if cached is not None:
                    return cached

                result = _original_method(self, *args, **kwargs)
                _set_cache(key, result)
                return result

            setattr(cls, method_name, cached_method)

        return cls

    return decorator


def _make_key(method_name: str, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    data = {
        "method": method_name,
        "args": args,
        "kwargs": tuple(sorted(kwargs.items())),
    }
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def _get_from_cache(key: str) -> Any:
    if key in _CACHE:
        entry = _CACHE[key]
        now = time.time()
        if now - entry.created_at < _CACHE_TTL:
            _CACHE[key].accessed_at = now
            return entry.value
        else:
            del _CACHE[key]
    return None


def _set_cache(key: str, value: Any) -> None:
    if len(_CACHE) >= _CACHE_MAX_SIZE:
        oldest = min(_CACHE, key=lambda k: _CACHE[k].accessed_at)
        del _CACHE[oldest]

    now = time.time()
    _CACHE[key] = CacheEntry(now, now, value)


@cache_methods(
    [
        "get_album",
        "get_artist",
        "get_artist_albums",
        "get_lyrics",
        "get_playlist",
        "get_watch_playlist",
        "search",
    ]
)
class CachedYTMusic(YTMusic):
    pass
