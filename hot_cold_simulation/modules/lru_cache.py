# type: ignore
import random
from collections import OrderedDict
from typing import Any, List


class LRUCache:
    def __init__(self, capacity: int, prepopulate=False):
        self.cache = OrderedDict()
        self.capacity = capacity
        if prepopulate:
            self.prepopulate_cache()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        else:
            return self.cache[key]

    def put(self, keys: List[int]) -> None:
        for key in keys:
            # Check if the cache is already full
            if len(self.cache) >= self.capacity:
                # Remove the least recently used item from the cache
                self.cache.popitem(last=False)

            # Add the new key or update the existing key, and move it to the end
            self.cache[key] = key
            self.cache.move_to_end(key)

    def prepopulate_cache(self) -> None:
        keys = random.sample(range(886), self.capacity)
        for key in keys:
            self.cache[key] = key

    def current_state(self) -> list[Any]:
        return list(self.cache.keys())
