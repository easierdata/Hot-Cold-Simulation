from collections import OrderedDict
from typing import Any


class TimeCache:
    def __init__(self, threshold):
        self.cache = OrderedDict()
        self.threshold = threshold

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        else:
            return self.cache[key][0]

    def put(self, key: int) -> None:
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

        # Put the new item in the cache with a counter of threshold
        self.cache[key] = (key, self.threshold)

    def current_state(self) -> list[Any]:
        return list(self.cache.keys())
