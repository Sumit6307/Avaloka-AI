"""
Comprehensive Unit Test Suite for Avaloka AI Assignment
=======================================================
Tests for:
1. Problem 1: LRU Cache (lru_cache.py)
2. Problem 2: Event Scheduler (event_scheduler.py)
3. Future Proofing: Room Assignment (room_allocator.py)
4. Concurrency: Thread-Safe LRU Cache (thread_safe_lru_cache.py)
"""

import pytest
import threading
import random
from lru_cache import LRUCache
from event_scheduler import can_attend_all, min_rooms_required, min_rooms_required_sweep_line
from room_allocator import assign_rooms, room_index_to_name
from thread_safe_lru_cache import ThreadSafeLRUCache


# ============================================================================
# PROBLEM 1 TESTS: LRU CACHE
# ============================================================================

class TestLRUCache:
    def test_basic_get_put(self):
        cache = LRUCache(2)
        cache.put(1, 10)
        cache.put(2, 20)
        assert cache.get(1) == 10
        assert cache.get(2) == 20
        assert cache.get(3) == -1

    def test_eviction_policy(self):
        cache = LRUCache(2)
        cache.put(1, 100)
        cache.put(2, 200)
        # Access 1 so 2 becomes least recently used
        assert cache.get(1) == 100
        # Insert 3 -> 2 should be evicted
        cache.put(3, 300)
        assert cache.get(2) == -1
        assert cache.get(1) == 100
        assert cache.get(3) == 300

    def test_update_existing_key(self):
        cache = LRUCache(2)
        cache.put(1, 10)
        cache.put(2, 20)
        # Update key 1 with new value
        cache.put(1, 99)
        assert cache.get(1) == 99
        # Inserting 3 should evict 2 (since 1 was just updated and is MRU)
        cache.put(3, 30)
        assert cache.get(2) == -1
        assert cache.get(1) == 99
        assert cache.get(3) == 30

    def test_capacity_one(self):
        cache = LRUCache(1)
        cache.put(1, 100)
        assert cache.get(1) == 100
        cache.put(2, 200)
        assert cache.get(1) == -1
        assert cache.get(2) == 200

    def test_invalid_capacity(self):
        with pytest.raises(ValueError):
            LRUCache(0)
        with pytest.raises(ValueError):
            LRUCache(-5)

    def test_recency_order_inspection(self):
        cache = LRUCache(3)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        assert cache.get_order_keys() == ["c", "b", "a"]
        cache.get("a")
        assert cache.get_order_keys() == ["a", "c", "b"]
        cache.put("d", 4)  # Evicts "b"
        assert cache.get_order_keys() == ["d", "a", "c"]
        assert cache.get("b") == -1


# ============================================================================
# PROBLEM 2 TESTS: EVENT SCHEDULER
# ============================================================================

class TestEventScheduler:
    def test_can_attend_all_empty_and_single(self):
        assert can_attend_all([]) is True
        assert can_attend_all([(9, 10)]) is True

    def test_can_attend_all_non_overlapping(self):
        # Adjacent events are permitted
        events = [(9, 10), (10, 11), (11, 12)]
        assert can_attend_all(events) is True

    def test_can_attend_all_unsorted_non_overlapping(self):
        events = [(11, 12), (9, 10), (10, 11)]
        assert can_attend_all(events) is True

    def test_can_attend_all_overlapping(self):
        events = [(9, 11), (10, 12)]
        assert can_attend_all(events) is False

    def test_can_attend_all_nested(self):
        events = [(9, 14), (10, 12)]
        assert can_attend_all(events) is False

    def test_invalid_event_interval(self):
        with pytest.raises(ValueError):
            can_attend_all([(10, 8)])

    def test_min_rooms_empty(self):
        assert min_rooms_required([]) == 0
        assert min_rooms_required_sweep_line([]) == 0

    def test_min_rooms_adjacent(self):
        # [(9, 10), (10, 11), (11, 12)] requires only 1 room
        events = [(9, 10), (10, 11), (11, 12)]
        assert min_rooms_required(events) == 1
        assert min_rooms_required_sweep_line(events) == 1

    def test_min_rooms_overlapping(self):
        # (9, 11) and (10, 12) overlap between 10 and 11
        events = [(9, 11), (10, 12), (11, 13)]
        # At t=10.5: (9, 11) and (10, 12) are active -> 2 rooms
        # At t=11: (9, 11) finishes, (11, 13) starts -> room can be reused!
        assert min_rooms_required(events) == 2
        assert min_rooms_required_sweep_line(events) == 2

    def test_min_rooms_all_concurrent(self):
        events = [(1, 10), (2, 9), (3, 8), (4, 7)]
        assert min_rooms_required(events) == 4
        assert min_rooms_required_sweep_line(events) == 4

    def test_min_rooms_staggered(self):
        events = [(0, 30), (5, 10), (15, 20)]
        # (0, 30) runs throughout. (5, 10) and (15, 20) don't overlap with each other,
        # but both overlap with (0, 30).
        # Peak concurrency is 2 rooms.
        assert min_rooms_required(events) == 2
        assert min_rooms_required_sweep_line(events) == 2


# ============================================================================
# FUTURE PROOFING TESTS: ROOM ALLOCATION
# ============================================================================

class TestRoomAllocator:
    def test_room_name_generation(self):
        assert room_index_to_name(1) == "Room A"
        assert room_index_to_name(2) == "Room B"
        assert room_index_to_name(26) == "Room Z"
        assert room_index_to_name(27) == "Room AA"

    def test_room_assignment_adjacent_reuse(self):
        events = [(9, 10), (10, 11), (11, 12)]
        result = assign_rooms(events)
        assert result["min_rooms"] == 1
        for item in result["assignments"]:
            assert item["room"] == "Room A"

    def test_room_assignment_concurrency_and_reuse(self):
        events = [(9, 11), (10, 12), (11, 13)]
        result = assign_rooms(events)
        assert result["min_rooms"] == 2
        # (9, 11) -> Room A
        # (10, 12) -> Room B
        # (11, 13) starts at 11, when (9, 11) finishes -> Room A freed and reused!
        assignments = {item["event"]: item["room"] for item in result["assignments"]}
        assert assignments[(9, 11)] == "Room A"
        assert assignments[(10, 12)] == "Room B"
        assert assignments[(11, 13)] == "Room A"


# ============================================================================
# CONCURRENCY TESTS: THREAD-SAFE LRU CACHE
# ============================================================================

class TestThreadSafeLRUCache:
    def test_multithreaded_read_write(self):
        cache = ThreadSafeLRUCache(50)
        num_threads = 10
        ops_per_thread = 500

        def worker(thread_id: int):
            for i in range(ops_per_thread):
                key = random.randint(1, 100)
                val = f"t{thread_id}_{i}"
                if random.random() < 0.6:
                    cache.put(key, val)
                else:
                    cache.get(key)

        threads = [threading.Thread(target=worker, args=(t,)) for t in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Cache size must not exceed capacity
        assert len(cache) <= 50

    def test_get_or_compute(self):
        cache = ThreadSafeLRUCache(10)
        calls = 0

        def compute(k):
            nonlocal calls
            calls += 1
            return f"computed_{k}"

        # First call computes
        val1 = cache.get_or_compute("x", compute)
        assert val1 == "computed_x"
        assert calls == 1

        # Second call hits cache
        val2 = cache.get_or_compute("x", compute)
        assert val2 == "computed_x"
        assert calls == 1  # Not computed again
