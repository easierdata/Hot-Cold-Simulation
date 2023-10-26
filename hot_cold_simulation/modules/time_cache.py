from collections import OrderedDict
from typing import Any


class TimeCache:
    def __init__(self, expiration_time: int):
        self.cache = OrderedDict()  # type: ignore
        self.expiration_time = expiration_time

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        else:
            return self.cache[key]

    def put(self, key: int) -> int:
        # Check if the cache is already full
        if len(self.cache) >= self.expiration_time:
            # Remove the first item from the cache
            self.cache.popitem(last=False)
        self.cache[key] = key
        return key

    def current_state(self) -> list[Any]:
        return list(self.cache.keys())
