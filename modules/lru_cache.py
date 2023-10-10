from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        else:
            # Move the accessed item to the end of the order
            self.cache.move_to_end(key)
            return self.cache[key]

    def put(self, key: int) -> int:
        # Check if the cache is already full
        if len(self.cache) >= self.capacity:
            # Remove the first item from the cache
            self.cache.popitem(last=False)
        self.cache[key] = key
        return key

    def current_state(self) -> list:
        return list(self.cache.keys())