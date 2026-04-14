import json
from typing import TypeVar, Optional, Callable
from django.core.cache import cache

T = TypeVar("T")


class CacheService:
    def __init__(self, default_timeout):
        self.default_timeout = default_timeout

    def set(self, key: str, value: T, timeout: Optional[int] = None) -> None:
        timeout = timeout or self.default_timeout

        try:
            serialized = json.dumps(value)
        except TypeError:
            raise Exception("Value must be JSON serializable")

        cache.set(key, serialized, timeout)

    def get(self, key: str) -> Optional[T]:
        data = cache.get(key)

        if data is None:
            return None

        try:
            return json.loads(data)
        except Exception:
            return None

    def get_or_set(self, key: str, factory: Callable[[], T], timeout: Optional[int] = None) -> T:
        data = self.get(key)

        if data is not None:
            return data

        value = factory()
        self.set(key, value, timeout)
        return value

    def delete(self, key: str) -> None:
        cache.delete(key)

    def clear(self) -> None:
        cache.clear()
