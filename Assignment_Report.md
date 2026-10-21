# Avaloka AI — Software Engineering Intern Assessment
## Data Structures & Systems Design

**Candidate Name:** Sumit Kesarwani  
**Email:** sumitkesar6307@gmail.com  
**Role:** Software Engineering Intern  
**Date:** October 2026  

---

## Table of Contents
1. [Problem 1: LRU Cache Implementation](#problem-1-lru-cache-implementation)
   - [Approach & Data Structure Selection in Plain English](#11-approach--data-structure-selection)
   - [Architectural Diagram](#12-architectural-diagram)
   - [Python Code Implementation](#13-python-code-implementation)
2. [Problem 2: Event Scheduler](#problem-2-event-scheduler)
   - [Algorithmic Logic in Plain English](#21-algorithmic-logic-in-plain-english)
   - [Interval Overlap & Room Calculation Logic](#22-interval-overlap--room-calculation-logic)
   - [Python Code Implementation](#23-python-code-implementation)
3. [Final Discussion & Analysis](#final-discussion--analysis)
   - [Time & Space Complexity Analysis](#31-time--space-complexity-analysis)
   - [Trade-off Analysis: Hash Map + Doubly Linked List](#32-trade-off-analysis-hash-map--doubly-linked-list)
   - [Future Proofing: Specific Room Assignment System](#33-future-proofing-specific-room-assignment-system)
   - [Concurrency & Thread Safety Deep Dive](#34-concurrency--thread-safety-deep-dive)
4. [Verification & Test Results](#4-verification--test-results)

---

## Problem 1: LRU Cache Implementation

### 1.1 Approach & Data Structure Selection

A **Least Recently Used (LRU) Cache** requires discarding the least recently accessed item when capacity is exceeded, while supporting $O(1)$ constant time for both `get` and `put` operations.

#### Why Choose a Hash Map combined with a Doubly Linked List?

To achieve strictly $O(1)$ time complexity for both `get` and `put`, we must satisfy two conflicting requirements simultaneously:
1. **Instant Key Lookup:** We must find any item by its key in $O(1)$ time. An array or linked list requires $O(N)$ sequential scanning, which is unacceptable. A **Hash Map (Python dictionary)** provides $O(1)$ average-time lookup from key to value.
2. **Instant Order Reorganization:** We must maintain chronological access order. When an item is accessed or added, it moves to the "Most Recently Used" (MRU) position. When the cache is full, the "Least Recently Used" (LRU) item must be evicted. In an array, removing an arbitrary element and shifting subsequent items takes $O(N)$ time.

A **Doubly Linked List (DLL)** is the ideal complementary data structure because:
- **$O(1)$ Removal of Any Node:** If we hold a direct reference to a node (provided by the Hash Map), we can decouple it in $O(1)$ time because each node contains both `prev` and `next` pointers:
  ```python
  node.prev.next = node.next
  node.next.prev = node.prev
  ```
  *(In contrast, a Singly Linked List cannot delete a node in $O(1)$ given only a pointer to that node, because finding the preceding node requires an $O(N)$ traversal from the head).*
- **$O(1)$ Head Insertion:** Inserting a newly created or promoted node right after the `head` is strictly $O(1)$.
- **$O(1)$ Tail Eviction:** The least recently used node is always immediately before the `tail` (`tail.prev`). Evicting it takes $O(1)$.

#### Sentinel (Dummy) Nodes Pattern
We initialize the Doubly Linked List with two sentinel nodes: `dummy_head` and `dummy_tail`, initially connected to each other (`head.next = tail`, `tail.prev = head`). Sentinel nodes eliminate boundary conditions: we never need to check if the list is empty, whether we are modifying the true head, or whether we are updating the true tail.

---

### 1.2 Architectural Diagram

```
                 HASH MAP (Key -> Node Reference)
                 +-------+-------------------------+
                 | Key 1 | -> Pointer to Node(1)   |
                 | Key 3 | -> Pointer to Node(3)   |
                 | Key 4 | -> Pointer to Node(4)   |
                 +-------+-------------------------+
                                    |
                                    v
               DOUBLY LINKED LIST (Recency Ordering)
  +----------+      +---------+      +---------+      +---------+      +----------+
  |  Dummy   | <->  | Node(4) | <->  | Node(1) | <->  | Node(3) | <->  |  Dummy   |
  |   Head   |      |  (MRU)  |      |         |      |  (LRU)  |      |   Tail   |
  +----------+      +---------+      +---------+      +---------+      +----------+
       ^                                                   ^
       |                                                   |
  New/Accessed items inserted here                Evicted from here when full
```

---

### 1.3 Python Code Implementation

```python
from typing import Any, Optional


class Node:
    """Doubly Linked List node storing key, value, and adjacent pointers."""

    def __init__(self, key: Any = 0, val: Any = 0):
        self.key: Any = key
        self.val: Any = val
        self.prev: Optional["Node"] = None
        self.next: Optional["Node"] = None

    def __repr__(self) -> str:
        return f"Node({self.key}: {self.val})"


class LRUCache:
    """
    Least Recently Used (LRU) Cache supporting O(1) get and put operations.
    """

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be a positive integer greater than 0.")
        self.capacity: int = capacity
        self.map: dict[Any, Node] = {}

        # Sentinel dummy nodes
        self.head: Node = Node()
        self.tail: Node = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node) -> None:
        """Decouples an existing node from the doubly linked list in O(1)."""
        prev_node = node.prev
        next_node = node.next
        if prev_node is not None and next_node is not None:
            prev_node.next = next_node
            next_node.prev = prev_node
        node.prev = None
        node.next = None

    def _add_to_head(self, node: Node) -> None:
        """Inserts a node right after the dummy head (marks as MRU) in O(1)."""
        node.next = self.head.next
        node.prev = self.head
        if self.head.next is not None:
            self.head.next.prev = node
        self.head.next = node

    def _move_to_head(self, node: Node) -> None:
        """Moves an existing node to the MRU position (head.next) in O(1)."""
        self._remove(node)
        self._add_to_head(node)

    def _pop_tail(self) -> Node:
        """Evicts and returns the least recently used node (tail.prev) in O(1)."""
        lru_node = self.tail.prev
        assert lru_node is not None and lru_node is not self.head, "Cache is empty."
        self._remove(lru_node)
        return lru_node

    def get(self, key: Any) -> Any:
        """
        Retrieves value for key if present, marking it as most recently used.
        Returns -1 if key does not exist.
        Time Complexity: O(1)
        """
        if key not in self.map:
            return -1

        node = self.map[key]
        self._move_to_head(node)
        return node.val

    def put(self, key: Any, value: Any) -> None:
        """
        Inserts or updates key-value pair. Evicts the LRU item if capacity is reached.
        Time Complexity: O(1)
        """
        if key in self.map:
            # Key exists: update value and promote to MRU
            node = self.map[key]
            node.val = value
            self._move_to_head(node)
        else:
            # Capacity check: evict least recently used node before insertion
            if len(self.map) >= self.capacity:
                lru_node = self._pop_tail()
                del self.map[lru_node.key]

            # Insert new node at head (MRU)
            new_node = Node(key, value)
            self.map[key] = new_node
            self._add_to_head(new_node)

    def __len__(self) -> int:
        return len(self.map)
```

---

## Problem 2: Event Scheduler

### 2.1 Algorithmic Logic in Plain English

The Event Scheduler problem handles interval scheduling for a meeting platform. Events are represented as `(start_time, end_time)` tuples. Crucially, **adjacent events (where `start_time == end_time`) do NOT count as overlaps**; a meeting ending at 10:00 AM frees the room exactly as the next meeting begins at 10:00 AM.

#### Function 1: `can_attend_all(events)`
- **Goal:** Determine if a single person can attend every scheduled event without any double-booking.
- **Approach:**
  1. If there are 0 or 1 events, no overlap is possible; return `True`.
  2. First validate that for every interval `start <= end`.
  3. Sort the events chronologically by `start_time`.
  4. Iterate through consecutive pairs of events: `events[i-1]` and `events[i]`.
  5. If the current meeting begins strictly before the previous meeting ends (`curr_start < prev_end`), the attendee would have to be in two places at once; return `False`.
  6. If `curr_start >= prev_end`, the attendee can transition smoothly. If all adjacent meetings satisfy this condition, return `True`.

#### Function 2: `min_rooms_required(events)`
- **Goal:** Find the minimum number of meeting rooms required to host all events simultaneously.
- **The Core Insight:** The minimum number of rooms needed across all time equals the **maximum number of concurrent, overlapping meetings** at any single instant.
- **Approach: Greedy Interval Partitioning with a Min-Heap:**
  1. Sort all meetings chronologically by `start_time`. This guarantees we examine events in the exact order they commence.
  2. Maintain a **Min-Heap** representing the active meeting rooms. Each element in the heap stores the `end_time` of an ongoing meeting in that room. The root of the min-heap (`heap[0]`) always represents the room that will be vacated earliest.
  3. For each event `(start, end)`:
     - Check if the earliest finishing meeting has completed by the time our current meeting starts (`heap[0] <= start`).
     - **If yes:** We don't need a new room! That existing room has just become available. We pop the old meeting's end time from the heap (reusing the room).
     - **If no:** All currently occupied rooms are still in use at time `start`. We must allocate a new room.
     - In either case, we push the current event's `end` time onto the heap to represent that the room is occupied until `end`.
  4. When all events have been processed, the size of the heap (`len(heap)`) reflects the maximum number of rooms simultaneously occupied.

---

### 2.2 Interval Overlap & Room Calculation Logic

Consider `events = [(9, 11), (10, 12), (11, 13)]`:
- Sorted Order: `(9, 11)`, `(10, 12)`, `(11, 13)`.
- **Event 1 `(9, 11)`:** Heap empty $\rightarrow$ allocate Room 1. Heap: `[11]`. Rooms = 1.
- **Event 2 `(10, 12)`:** Starts at 10. Earliest free time is 11 (`11 > 10`). Cannot reuse. Allocate Room 2. Heap: `[11, 12]`. Rooms = 2.
- **Event 3 `(11, 13)`:** Starts at 11. Earliest free time is 11 (`11 <= 11`). Room 1 is free! Pop 11, push 13. Heap: `[12, 13]`. Rooms = 2.
- **Result:** Minimum rooms required = 2.

---

### 2.3 Python Code Implementation

```python
import heapq
from typing import List, Tuple

Event = Tuple[int, int]


def can_attend_all(events: List[Event]) -> bool:
    """
    Returns True if a person can attend all events without overlaps, False otherwise.
    Adjacent events (end == start) are permitted.
    """
    # Validate intervals
    for s, e in events:
        if s > e:
            raise ValueError(f"Invalid event interval: start ({s}) > end ({e}).")

    if len(events) <= 1:
        return True

    # Sort events chronologically by start time
    sorted_events = sorted(events, key=lambda ev: ev[0])

    for i in range(1, len(sorted_events)):
        prev_end = sorted_events[i - 1][1]
        curr_start = sorted_events[i][0]

        # Strict inequality: adjacent events (curr_start == prev_end) do NOT overlap
        if curr_start < prev_end:
            return False

    return True


def min_rooms_required(events: List[Event]) -> int:
    """
    Returns the minimum number of meeting rooms required to schedule all events.
    Uses a Min-Heap of room end times to greedily reuse rooms.
    """
    if not events:
        return 0

    # Sort events chronologically by start time
    sorted_events = sorted(events, key=lambda ev: ev[0])

    # Min-heap tracking end times of currently active rooms
    room_end_times: List[int] = []

    for start, end in sorted_events:
        if start > end:
            raise ValueError(f"Invalid event interval: start ({start}) > end ({end}).")

        # If the earliest ending meeting has finished on or before current start time,
        # reuse that room.
        if room_end_times and room_end_times[0] <= start:
            heapq.heappop(room_end_times)

        # Allocate room (reused or newly created)
        heapq.heappush(room_end_times, end)

    return len(room_end_times)
```

---

## Final Discussion & Analysis

### 3.1 Time & Space Complexity Analysis

| Function / Component | Time Complexity (Best / Avg / Worst) | Space Complexity (Auxiliary) | Justification |
| :--- | :--- | :--- | :--- |
| **`LRUCache.get(key)`** | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | Hash table lookup is $\mathcal{O}(1)$ average. Moving the node to the DLL head involves updating 4 pointers, which is strictly $\mathcal{O}(1)$. |
| **`LRUCache.put(key, val)`** | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ per op / $\mathcal{O}(C)$ overall | Hash table insertion/update is $\mathcal{O}(1)$. Evicting the tail node and adding a new node to the head involves constant pointer manipulations. Total space is bounded by cache capacity $C$. |
| **`can_attend_all(events)`** | $\mathcal{O}(N \log N)$ | $\mathcal{O}(N)$ | Sorting $N$ event tuples by start time dominates at $\mathcal{O}(N \log N)$. The subsequent linear scan checks $N-1$ adjacent intervals in $\mathcal{O}(N)$ time. |
| **`min_rooms_required(events)`** | $\mathcal{O}(N \log N)$ | $\mathcal{O}(N)$ | Sorting events requires $\mathcal{O}(N \log N)$. For each of the $N$ events, min-heap push and conditional pop take $\mathcal{O}(\log K)$, where $K \le N$ is the maximum number of concurrent rooms. Total time is $\mathcal{O}(N \log N + N \log K) = \mathcal{O}(N \log N)$. Heap space is at most $K \le N$. |

---

### 3.2 Trade-off Analysis: Hash Map + Doubly Linked List

Why is this specific pairing the industry standard for LRU Caches? We analyze the trade-offs against alternative data structure configurations:

| Architecture | Lookup Time | Recency Update Time | Eviction Time | Total Time per Op | Primary Disadvantage / Trade-off |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Hash Map + Doubly Linked List** | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | $\mathbf{\mathcal{O}(1)}$ | **Higher memory overhead:** Each node requires 4 pointers (`prev`, `next`, `key`, `val`), plus hash table bucket pointers. Node allocations also cause pointer indirection and cache line misses. |
| **Hash Map + Array / Dynamic List** | $\mathcal{O}(1)$ | $\mathcal{O}(N)$ | $\mathcal{O}(N)$ | $\mathcal{O}(N)$ | Moving an accessed element to the end of an array requires shifting elements ($\mathcal{O}(N)$). Evicting index 0 also requires an $\mathcal{O}(N)$ shift. |
| **Hash Map + Singly Linked List** | $\mathcal{O}(1)$ | $\mathcal{O}(N)$ | $\mathcal{O}(1)$ | $\mathcal{O}(N)$ | Given a pointer to a node, removing it requires updating the *previous* node's `next` pointer. Without a `prev` pointer, finding the preceding node takes an $\mathcal{O}(N)$ scan from the head. |
| **Hash Map + Min-Heap (Timestamps)** | $\mathcal{O}(1)$ | $\mathcal{O}(\log N)$ or $\mathcal{O}(N)$ | $\mathcal{O}(\log N)$ | $\mathcal{O}(\log N)$ | Updating a node's timestamp on `get()` requires a decrease/increase-key operation in the heap, requiring index tracking or $\mathcal{O}(N)$ search. |
| **Doubly Linked List Alone** | $\mathcal{O}(N)$ | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | $\mathcal{O}(N)$ | Finding an item by key requires a sequential scan from head to tail ($\mathcal{O}(N)$). |

**Engineering Verdict:** The Hash Map + Doubly Linked List combination is chosen because it is the **only architecture that guarantees strictly $\mathcal{O}(1)$ execution for all operations**. The trade-off is higher memory consumption per entry, which is virtually always acceptable in high-performance computing to eliminate latency spikes.

---

### 3.3 Future Proofing: Specific Room Assignment System

#### Requirement
In a production scheduling system, knowing the *count* of rooms is insufficient; the platform must output the exact room assigned to each meeting (e.g., Event $(9, 11) \rightarrow$ "Room A", Event $(10, 12) \rightarrow$ "Room B", Event $(11, 13) \rightarrow$ "Room A").

#### Architectural Design
To assign specific, reusable room labels while minimizing the number of rooms:
1. **Preserve Original Event Order:** Pair each event with its input index `(start, end, index)` before sorting.
2. **Dual-Heap Architecture:**
   - `active_rooms_heap`: A Min-Heap storing `(end_time, room_id)`. The root always tells us which room finishes next.
   - `free_rooms_heap`: A Min-Heap storing idle room IDs (e.g., `[1, 2, ...]`). Using a min-heap guarantees we always prioritize reusing lower-numbered rooms first (e.g., reusing "Room A" before opening "Room C").
3. **Execution Flow:**
   - When an event starts at time `start`, inspect `active_rooms_heap`. For every meeting with `end_time <= start`, pop it and push its `room_id` into `free_rooms_heap`.
   - If `free_rooms_heap` is non-empty, pop the lowest room ID (reusing an existing room).
   - If `free_rooms_heap` is empty, increment `room_counter` and assign a newly created room.
   - Map room ID to human-readable names: $1 \rightarrow \text{"Room A"}$, $2 \rightarrow \text{"Room B"}$, $26 \rightarrow \text{"Room Z"}$, $27 \rightarrow \text{"Room AA"}$.
   - Push `(end_time, assigned_room_id)` to `active_rooms_heap`.

#### Concrete Implementation
```python
import heapq
from typing import List, Tuple, Dict, Any


def room_index_to_name(index: int) -> str:
    """Converts 1 -> 'Room A', 2 -> 'Room B', 27 -> 'Room AA'."""
    name = ""
    curr = index
    while curr > 0:
        curr -= 1
        name = chr(ord('A') + (curr % 26)) + name
        curr //= 26
    return f"Room {name}"


def assign_rooms(events: List[Tuple[int, int]]) -> Dict[str, Any]:
    if not events:
        return {"min_rooms": 0, "assignments": []}

    indexed_events = [(ev[0], ev[1], i) for i, ev in enumerate(events)]
    indexed_events.sort(key=lambda x: (x[0], x[1]))

    active_rooms_heap: List[Tuple[int, int]] = []  # (end_time, room_id)
    free_rooms_heap: List[int] = []  # available room IDs
    total_rooms_created = 0
    assignments = [""] * len(events)

    for start, end, orig_idx in indexed_events:
        # Free rooms that concluded on or before current start time
        while active_rooms_heap and active_rooms_heap[0][0] <= start:
            _, freed_room = heapq.heappop(active_rooms_heap)
            heapq.heappush(free_rooms_heap, freed_room)

        # Allocate room: reuse lowest freed room or create new one
        if free_rooms_heap:
            room_id = heapq.heappop(free_rooms_heap)
        else:
            total_rooms_created += 1
            room_id = total_rooms_created

        heapq.heappush(active_rooms_heap, (end, room_id))
        assignments[orig_idx] = room_index_to_name(room_id)

    return {
        "min_rooms": total_rooms_created,
        "assignments": [
            {"event": events[i], "room": assignments[i]} for i in range(len(events))
        ]
    }
```

---

### 3.4 Concurrency & Thread Safety Deep Dive

#### Why Standard LRU Cache Fails in Concurrent Environments
1. **The `get(key)` Mutation Hazard:** In standard caching, read operations are typically idempotent. However, in an LRU cache, **`get()` is inherently a write operation**. Accessing an item unlinks it from its current position in the Doubly Linked List and relinks it at the head. If Thread A and Thread B concurrently call `get()` on different keys:
   - Pointer manipulations (`node.prev.next = node.next`) execute out-of-order.
   - Pointers can overwrite each other, causing circular references (infinite loops during iteration), disconnected nodes (silent memory leaks), or `AttributeError: 'NoneType' object has no attribute 'prev'`.
2. **The `put(key, val)` Race Condition:**
   - If two threads detect that capacity is reached at the same instant, both may attempt to pop `tail.prev`, evicting two items when only one was required.
   - Concurrent writes to Python dictionaries without synchronization can lead to corrupted hash table buckets.

#### Concurrency Solutions & Architecture Evolution

##### 1. Coarse-Grained Synchronization (`threading.RLock`)
- **Mechanism:** Wrap all public methods (`get`, `put`, `len`) inside a reentrant lock (`with self._lock:`).
- **Pros:** 100% thread-safe, prevents race conditions, deadlocks, and corrupted pointers.
- **Cons:** High lock contention under heavy concurrent workloads; serializes all operations.

##### 2. Read-Write Lock with Asynchronous Recency Buffering (Caffeine / Guava Pattern)
- In production scale (e.g., high-throughput backend services), acquiring an exclusive lock on every `get()` degrades throughput.
- **Modern Solution:**
  - Decouple the read from the recency reordering.
  - The hash map is protected by a fast Concurrent Hash Map or Read-Write Lock (`RWLock`).
  - When `get(key)` is invoked, the thread reads the value without acquiring an exclusive lock. Instead of updating the linked list immediately, it pushes a small event record `AccessEvent(key)` into a high-speed, lock-free ring buffer (Lossy / MPSC Buffer).
  - A dedicated background thread (or periodic batched drain) consumes events from the ring buffer and applies recency updates to the Doubly Linked List in batches.

##### 3. Lock Striping (Sharded Cache)
- Divide the cache into $K$ independent shards (e.g., $K = 16$ or $32$), where each shard has its own capacity ($C/K$), its own hash map, its own doubly linked list, and its own mutex.
- A key is routed via `shard_id = hash(key) % K`.
- Contention is reduced by a factor of $K$, scaling linearly with CPU core counts.

##### 4. Cache Stampede Prevention (`get_or_compute`)
- In production, when a cache miss occurs under high concurrency, 50 threads might simultaneously query the backend database for the same key.
- A production thread-safe cache provides an atomic `get_or_compute(key, loader_fn)`: if the key is missing, only one thread executes the expensive loader function while subsequent threads wait and receive the cached result.

---

## 4. Verification & Test Results

The implementation was validated against a comprehensive test suite covering edge cases, property invariants, and multi-threaded stress tests (`test_assignment.py`):

```
test_assignment.py::TestLRUCache::test_basic_get_put PASSED              [  4%]
test_assignment.py::TestLRUCache::test_eviction_policy PASSED            [  9%]
test_assignment.py::TestLRUCache::test_update_existing_key PASSED        [ 13%]
test_assignment.py::TestLRUCache::test_capacity_one PASSED               [ 18%]
test_assignment.py::TestLRUCache::test_invalid_capacity PASSED           [ 22%]
test_assignment.py::TestLRUCache::test_recency_order_inspection PASSED   [ 27%]
test_assignment.py::TestEventScheduler::test_can_attend_all_empty_and_single PASSED [ 31%]
test_assignment.py::TestEventScheduler::test_can_attend_all_non_overlapping PASSED [ 36%]
test_assignment.py::TestEventScheduler::test_can_attend_all_unsorted_non_overlapping PASSED [ 40%]
test_assignment.py::TestEventScheduler::test_can_attend_all_overlapping PASSED [ 45%]
test_assignment.py::TestEventScheduler::test_can_attend_all_nested PASSED [ 50%]
test_assignment.py::TestEventScheduler::test_invalid_event_interval PASSED [ 54%]
test_assignment.py::TestEventScheduler::test_min_rooms_empty PASSED      [ 59%]
test_assignment.py::TestEventScheduler::test_min_rooms_adjacent PASSED   [ 63%]
test_assignment.py::TestEventScheduler::test_min_rooms_overlapping PASSED [ 68%]
test_assignment.py::TestEventScheduler::test_min_rooms_all_concurrent PASSED [ 72%]
test_assignment.py::TestEventScheduler::test_min_rooms_staggered PASSED  [ 77%]
test_assignment.py::TestRoomAllocator::test_room_name_generation PASSED  [ 81%]
test_assignment.py::TestRoomAllocator::test_room_assignment_adjacent_reuse PASSED [ 86%]
test_assignment.py::TestRoomAllocator::test_room_assignment_concurrency_and_reuse PASSED [ 90%]
test_assignment.py::TestThreadSafeLRUCache::test_multithreaded_read_write PASSED [ 95%]
test_assignment.py::TestThreadSafeLRUCache::test_get_or_compute PASSED   [100%]

============================= 22 passed in 0.06s ==============================
```

All 22 test cases passed seamlessly.
