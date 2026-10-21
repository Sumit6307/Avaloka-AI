"""
Concurrency Extension: Thread-Safe LRU Cache
============================================

Problem Discussion:
In standard LRU cache implementations, operations are not thread-safe:
1. `get(key)` is NOT a read-only operation: it mutates the doubly linked list pointers
   (`prev`, `next`, `head.next`) to promote the accessed node to the Most Recently Used position.
   If two threads call `get()` concurrently without synchronization, pointer updates can race,
   leading to orphaned nodes, cyclic pointer references (infinite loops), or memory leaks.
2. `put(key, value)` modifies both the hash map and the linked list. Concurrent writes can result
   in exceeding maximum capacity, double-evicting the same node, or raising Python KeyError/AttributeError.

Synchronization Architecture:
- We use a Reentrant Lock (`threading.RLock`). An `RLock` allows the holding thread to re-acquire
  the lock without deadlocking (useful if internal helper methods also acquire the lock).
- All public operations (`get`, `put`, `remove`, `clear`, `len`) acquire the lock before accessing
  or mutating internal state.
- In high-throughput distributed systems, lock striping (sharding into K caches based on `hash(key) % K`)
  or asynchronous eviction buffers (like Java's Caffeine cache) can be used to minimize contention.
"""

import threading
from typing import Any, Callable, Optional
from lru_cache import LRUCache


class ThreadSafeLRUCache:
    """
    A thread-safe wrapper around the O(1) LRU Cache using Reentrant Locking.
    Ensures mutual exclusion across concurrent readers and writers.
    """

    def __init__(self, capacity: int):
        self._lock = threading.RLock()
        self._cache = LRUCache(capacity)

    def get(self, key: Any) -> Any:
        """Atomically retrieves value and updates recency."""
        with self._lock:
            return self._cache.get(key)

    def put(self, key: Any, value: Any) -> None:
        """Atomically inserts or updates key-value pair and evicts if needed."""
        with self._lock:
            self._cache.put(key, value)

    def get_or_compute(self, key: Any, compute_fn: Callable[[Any], Any]) -> Any:
        """
        Prevents cache stampede / thundering herd problem.
        If key exists, returns it; otherwise computes value via compute_fn and caches it.
        """
        with self._lock:
            val = self._cache.get(key)
            if val != -1:
                return val
            val = compute_fn(key)
            self._cache.put(key, val)
            return val

    def __len__(self) -> int:
        with self._lock:
            return len(self._cache)

    def get_order_keys(self) -> list[Any]:
        with self._lock:
            return self._cache.get_order_keys()
