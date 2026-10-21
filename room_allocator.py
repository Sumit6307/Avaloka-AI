"""
Future-Proofing Extension: Event Scheduler with Explicit Room Assignment
========================================================================

Problem Extension:
Modify the event scheduler to not only compute the minimum number of rooms,
but also assign specific, reusable room identifiers (e.g., "Room A", "Room B", "Room C")
to each event without time collisions.

Algorithmic Logic:
1. Sort events chronologically by start time. To preserve the original event identities
   and return the assignments in the caller's order, track original indices: (start, end, original_idx).
2. Maintain:
   - `active_rooms_heap`: A min-heap storing tuples of `(end_time, room_number)`.
     The root always holds the meeting finishing earliest.
   - `free_rooms_heap`: A min-heap storing available room numbers currently unassigned.
     Using a min-heap guarantees that the lowest-numbered room is always reused first,
     packing events into minimal rooms (e.g., Room A before Room B).
3. For each event (start, end):
   - Check `active_rooms_heap`. While the top meeting has concluded (`end_time <= start`),
     pop it and push its `room_number` into `free_rooms_heap`.
   - If `free_rooms_heap` has rooms, pop the lowest room number (reuse).
   - If `free_rooms_heap` is empty, allocate a new room number: `new_room_number = total_rooms_created + 1`.
   - Assign this room to the event.
   - Push `(end_time, assigned_room)` into `active_rooms_heap`.
4. Return both the total distinct room count and the detailed schedule mapping
   each event to its assigned room name (e.g. "Room A", "Room B").
"""

import heapq
from typing import List, Tuple, Dict, Any

Event = Tuple[int, int]


def room_index_to_name(index: int) -> str:
    """
    Converts 1-based room index to alphabet room names:
    1 -> 'Room A', 2 -> 'Room B', ..., 26 -> 'Room Z', 27 -> 'Room AA', etc.
    """
    name = ""
    curr = index
    while curr > 0:
        curr -= 1
        name = chr(ord('A') + (curr % 26)) + name
        curr //= 26
    return f"Room {name}"


def assign_rooms(events: List[Event]) -> Dict[str, Any]:
    """
    Schedules events into specific rooms such that no room has overlapping events,
    while minimizing the total number of distinct rooms used.

    Args:
        events: List of (start_time, end_time) tuples.

    Returns:
        Dict containing:
        - "min_rooms": Total number of distinct rooms allocated.
        - "assignments": List of dicts with original event, assigned room name, and time.
        - "room_schedules": Dict mapping room name to list of events hosted in that room.
    """
    if not events:
        return {
            "min_rooms": 0,
            "assignments": [],
            "room_schedules": {}
        }

    # Attach original index to retain caller's input order in final report
    indexed_events = [
        (ev[0], ev[1], idx) for idx, ev in enumerate(events)
    ]

    # Sort primarily by start time; secondary sort by end time
    indexed_events.sort(key=lambda x: (x[0], x[1]))

    # Min-heap of currently occupied rooms: stores (end_time, room_num)
    active_rooms_heap: List[Tuple[int, int]] = []

    # Min-heap of idle/freed room numbers available for immediate reuse
    free_rooms_heap: List[int] = []

    total_rooms_created = 0
    # Store result by original index
    event_room_assignment: List[Tuple[int, str]] = [("", "")] * len(events)

    for start, end, orig_idx in indexed_events:
        if start > end:
            raise ValueError(f"Invalid event interval: ({start}, {end})")

        # Free all rooms whose meetings have finished on or before current start time
        while active_rooms_heap and active_rooms_heap[0][0] <= start:
            _, freed_room_num = heapq.heappop(active_rooms_heap)
            heapq.heappush(free_rooms_heap, freed_room_num)

        # Allocate room: prefer lowest free room, or create new room if none free
        if free_rooms_heap:
            assigned_room_num = heapq.heappop(free_rooms_heap)
        else:
            total_rooms_created += 1
            assigned_room_num = total_rooms_created

        # Mark active until `end`
        heapq.heappush(active_rooms_heap, (end, assigned_room_num))

        room_name = room_index_to_name(assigned_room_num)
        event_room_assignment[orig_idx] = (assigned_room_num, room_name)

    # Format output for caller
    assignments = []
    room_schedules: Dict[str, List[Event]] = {}

    for idx, (room_num, room_name) in enumerate(event_room_assignment):
        ev = events[idx]
        assignments.append({
            "event_index": idx,
            "event": ev,
            "room": room_name
        })
        if room_name not in room_schedules:
            room_schedules[room_name] = []
        room_schedules[room_name].append(ev)

    # Sort each room's schedule chronologically
    for r_name in room_schedules:
        room_schedules[r_name].sort(key=lambda x: x[0])

    return {
        "min_rooms": total_rooms_created,
        "assignments": assignments,
        "room_schedules": room_schedules
    }


if __name__ == "__main__":
    test_events = [(9, 11), (10, 12), (11, 13), (12, 14)]
    result = assign_rooms(test_events)
    print("Room Assignment Result:")
    print(f"Total Rooms Required: {result['min_rooms']}")
    for item in result["assignments"]:
        print(f"  Event {item['event']} -> {item['room']}")
    print("\nRoom Schedules:")
    for room, sched in result["room_schedules"].items():
        print(f"  {room}: {sched}")
