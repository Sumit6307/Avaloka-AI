# Avaloka AI — Data Structures & Systems Design Technical Assessment

**Candidate:** Sumit Kesarwani  
**Email:** sumitkesar6307@gmail.com  
**Role:** Software Engineering Intern  
**Repository Contents:** Solutions to Problem 1 (LRU Cache), Problem 2 (Event Scheduler), Extensions (Future-Proofing & Concurrency), Pytest Suite, and PDF Deliverable.

---

## 📁 Repository Structure

```
.
├── lru_cache.py                          # Problem 1: O(1) LRU Cache (Hash Map + Doubly Linked List)
├── event_scheduler.py                    # Problem 2: Event Scheduler (can_attend_all & min_rooms_required)
├── room_allocator.py                     # Future-Proofing: Specific Room Label Assignment (Room A, Room B)
├── thread_safe_lru_cache.py              # Concurrency: Thread-Safe LRU Cache with RLock & Stampede Protection
├── test_assignment.py                    # Comprehensive Pytest Suite (22 test cases, 100% pass)
├── Assignment_Report.md                  # Complete written technical report and analysis
├── generate_pdf.py                       # Automated PDF generator script using ReportLab
├── Sumit_Kesarwani_Avaloka_Assignment.pdf # Executive PDF submission deliverable
└── README.md                             # Documentation & instructions
```

---

## 🚀 Quick Start & Verification

### 1. Run the Entire Test Suite
Execute all 22 unit tests covering boundary conditions, edge cases, interval collisions, room reuse, and multi-threaded stress tests:
```bash
python -m pytest -v
```

### 2. Run Individual Modules
```bash
# Problem 1: LRU Cache
python lru_cache.py

# Problem 2: Event Scheduler
python event_scheduler.py

# Extension: Specific Room Allocation
python room_allocator.py
```

### 3. Regenerate or Customize PDF
To recompile the PDF or customize the author name:
```bash
python generate_pdf.py Custom_Name_Avaloka_Assignment.pdf
```

---

## 📋 Overview of Solutions

### Problem 1: LRU Cache (`lru_cache.py`)
- **Operations:**
  - `get(key)`: Returns value or `-1` if absent, promoting accessed item to Most Recently Used (MRU).
  - `put(key, value)`: Inserts or updates item. Evicts the Least Recently Used (LRU) item if capacity is reached.
- **Time Complexity:** Strict $\mathcal{O}(1)$ for both `get` and `put`.
- **Data Structures:** Hash Map (for $\mathcal{O}(1)$ key-to-node lookup) + Doubly Linked List with Sentinel nodes (for $\mathcal{O}(1)$ node unlinking, MRU insertion, and LRU tail eviction).

### Problem 2: Event Scheduler (`event_scheduler.py`)
- **Operations:**
  - `can_attend_all(events)`: Returns `True` if all events can be attended without overlaps, `False` otherwise. Adjacent events (`end == start`) are permitted per specification. Time complexity $\mathcal{O}(N \log N)$.
  - `min_rooms_required(events)`: Greedily tracks concurrent active room usage using a Min-Heap of end times. Time complexity $\mathcal{O}(N \log N)$.

### Future-Proofing: Specific Room Assignment (`room_allocator.py`)
- Extends the scheduler to allocate explicit, human-readable room labels (e.g., `"Room A"`, `"Room B"`, `"Room C"`).
- Uses a **Dual-Heap Architecture** (`active_rooms_heap` and `free_rooms_heap`) to prioritize reusing lower-indexed rooms first while strictly preventing room double-booking.

### Concurrency: Thread-Safe LRU Cache (`thread_safe_lru_cache.py`)
- Addresses race conditions on both `get` (which mutates DLL pointers) and `put` (which mutates hash map and can double-evict).
- Implements `threading.RLock` mutual exclusion and provides atomic `get_or_compute` to protect against cache stampedes / thundering herds.
- Discusses production scaling patterns: Read-Write Locks with asynchronous recency ring buffers (Caffeine / Guava) and Lock Striping / Sharded Caches.

---

## 📊 Complexity Summary Table

| Function | Time Complexity | Space Complexity | Description |
| :--- | :---: | :---: | :--- |
| `LRUCache.get(key)` | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | Hash lookup + DLL pointer update |
| `LRUCache.put(key, val)` | $\mathcal{O}(1)$ | $\mathcal{O}(C)$ | Hash insertion + DLL head insert / tail evict |
| `can_attend_all(events)` | $\mathcal{O}(N \log N)$ | $\mathcal{O}(N)$ | Sort by start time + linear adjacent scan |
| `min_rooms_required(events)` | $\mathcal{O}(N \log N)$ | $\mathcal{O}(N)$ | Sort by start time + Min-Heap room reuse |
| `assign_rooms(events)` | $\mathcal{O}(N \log N)$ | $\mathcal{O}(N)$ | Dual Min-Heap with free-room reuse |
