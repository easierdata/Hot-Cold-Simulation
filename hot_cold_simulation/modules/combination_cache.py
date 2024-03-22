# type: ignore
import random
import threading
from collections import OrderedDict
from typing import Any, List


class CombinationCache:
    def __init__(self, capacity: int, expiration_time=10, prepopulate=False):
        self.cache = OrderedDict()
        self.capacity = capacity
        self.expiration_time = expiration_time
        self.lock = threading.Lock()
        if prepopulate:
            self.prepopulate_cache()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        else:
            return self.cache[key][0]

    def put(self, keys: List[int]) -> None:
        with self.lock:
            # Update the counter of existing items
            keys_to_delete = []
            for k, (value, count) in self.cache.items():
                if count <= 1:
                    keys_to_delete.append(k)
                else:
                    self.cache[k] = (value, count - 1)

            # Remove items whose counter has reached zero
            for k in keys_to_delete:
                del self.cache[k]

            for key in keys:
                # Check if the cache is already full
                if len(self.cache) >= self.capacity:
                    # Remove the least recently used item from the cache
                    self.cache.popitem(last=False)

                # Put the new items in the cache with a counter of expiration_time
                self.cache[key] = (key, self.expiration_time)
                self.cache.move_to_end(key)

    def prepopulate_cache(self) -> None:
        keys = random.sample(range(886), self.capacity)
        for key in keys:
            self.cache[key] = (key, self.expiration_time)

    def current_state(self) -> list[Any]:
        return list(self.cache.keys())
