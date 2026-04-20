from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Generic, TypeVar


T = TypeVar("T")


@dataclass
class CacheEntry(Generic[T]):
    value: T
    expires_at: float
    stale_expires_at: float


class TTLCache(Generic[T]):
    def __init__(self) -> None:
        self._store: dict[str, CacheEntry[T]] = {}

    def get(self, key: str) -> T | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        if time.time() > entry.expires_at:
            return None
        return entry.value

    def get_stale(self, key: str) -> T | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        if time.time() > entry.stale_expires_at:
            self._store.pop(key, None)
            return None
        return entry.value

    def set(self, key: str, value: T, ttl_seconds: int, stale_ttl_seconds: int) -> None:
        now = time.time()
        self._store[key] = CacheEntry(
            value=value,
            expires_at=now + ttl_seconds,
            stale_expires_at=now + max(ttl_seconds, stale_ttl_seconds),
        )
