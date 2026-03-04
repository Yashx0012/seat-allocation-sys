"""
core/lru_cache.py - Thread-safe LRU cache backed by OrderedDict.

Stores arbitrary plan-entry objects keyed by filename.
Least-recently-used entry is evicted when maxsize is exceeded.
"""

import threading
from collections import OrderedDict


class LRUCache:
    """
    Thread-safe LRU cache.

    Parameters
    ----------
    maxsize : int
        Maximum number of entries to keep in memory simultaneously.
        When full, the least-recently-used entry is evicted.
    """

    def __init__(self, maxsize: int = 5) -> None:
        self._cache: OrderedDict = OrderedDict()
        self._maxsize = maxsize
        self._lock = threading.Lock()
        self.hits   = 0
        self.misses = 0

    # ── public API ────────────────────────────────────────────────────────────

    def get(self, key: str):
        """Return cached value or None on miss. Moves key to MRU position."""
        with self._lock:
            if key not in self._cache:
                self.misses += 1
                return None
            self._cache.move_to_end(key)   # mark as most-recently-used
            self.hits += 1
            return self._cache[key]

    def put(self, key: str, value) -> None:
        """Insert or refresh an entry. Evicts LRU entry if over capacity."""
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = value
            if len(self._cache) > self._maxsize:
                evicted_key, _ = self._cache.popitem(last=False)   # remove LRU
                import logging
                logging.getLogger(__name__).debug(
                    f"LRU evicted: {evicted_key}"
                )

    def evict(self, key: str) -> None:
        """Explicitly remove an entry (e.g. after a file is deleted)."""
        with self._lock:
            self._cache.pop(key, None)

    def clear(self) -> None:
        """Remove all entries and reset hit / miss counters."""
        with self._lock:
            self._cache.clear()
            self.hits   = 0
            self.misses = 0

    def keys(self) -> list:
        """Return a snapshot of currently cached keys (MRU → LRU order)."""
        with self._lock:
            return list(reversed(self._cache.keys()))

    def stats(self) -> dict:
        """Return hit/miss/size statistics."""
        with self._lock:
            total    = self.hits + self.misses
            hit_rate = round(self.hits / total, 3) if total else 0.0
            return {
                "hits":     self.hits,
                "misses":   self.misses,
                "hit_rate": hit_rate,
                "size":     len(self._cache),
                "maxsize":  self._maxsize,
                "cached":   list(reversed(self._cache.keys())),
            }
