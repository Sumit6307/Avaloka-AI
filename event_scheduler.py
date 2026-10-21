"""
Problem 2: Event Scheduler Implementation
==========================================

Problem Statement:
Design a meeting scheduling system. Given a list of events represented as (start_time, end_time) tuples:
1. can_attend_all(events): Returns True if a single person can attend all events without overlaps,
   False otherwise.
2. min_rooms_required(events): Returns the minimum number of meeting rooms required to schedule
   all events simultaneously.

Constraints & Assumptions:
- Input format: list of tuples, e.g. [(9, 10), (10, 11), (11, 12)]
- Adjacent events (where start_time == end_time) do NOT overlap.
  Example: (9, 10) and (10, 11) can be attended by the same person in the same room.

Algorithmic Logic Explanation:
------------------------------
1. can_attend_all(events):
   - A single person can attend all meetings if and only if no two meetings conflict in time.
   - Sort events primarily by start time in ascending order.
   - Iterate through the sorted list and compare each meeting's start time with the preceding meeting's
     end time.
   - If `current_start < previous_end`, an overlap exists, so the person cannot attend both -> return False.
   - If `current_start >= previous_end`, there is no conflict. Note that `current_start == previous_end`
     is explicitly allowed per problem constraints.
   - If all adjacent pairs pass with no conflict, return True.

2. min_rooms_required(events):
   - The problem asks for the maximum number of concurrent meetings occurring at any point in time.
   - Algorithmic Approach: Greedy Interval Scheduling using a Min-Heap.
     a. If the list is empty, 0 rooms are required.
     b. Sort all events chronologically by start time.
     c. Maintain a min-heap of active room end times. The root of the min-heap always contains
        the meeting that concludes earliest among all ongoing meetings.
     d. For each event (start, end) in sorted order:
        - Check if the earliest finishing meeting (`heap[0]`) has ended by the current meeting's start time:
          `heap[0] <= start`.
        - If so, that existing room is freed up and can be reused. We pop the earliest end time from the heap.
        - If not, all currently occupied rooms are still in use, so a new room must be allocated.
        - Push the current meeting's end time onto the heap (`heappush(heap, end)`).
     e. By the end of processing, the total number of items remaining in the heap equals the minimum
        number of rooms required.
     - Why this works: Greedily reassigning the room that frees up earliest leaves room for incoming
       meetings without ever allocating an unnecessary room.

   - Alternative / Complementary Perspective (Sweep-Line / Two-Pointer Technique):
     - Separate all start times and end times into two sorted arrays.
     - Move through time: whenever a meeting starts before the earliest meeting ends (`start < end`),
       increment the room count. When an end time is reached (`start >= end`), decrement room count.
     - The peak room count observed during the sweep is the minimum rooms required.
     - Both algorithms run in O(N log N) time and O(N) space. The min-heap approach additionally provides
       a seamless path to assign explicit room identifiers (e.g. Room A, Room B).
"""

import heapq
from typing import List, Tuple

Event = Tuple[int, int]


def can_attend_all(events: List[Event]) -> bool:
    """
    Determines whether a person can attend all scheduled events without conflict.

    Args:
        events: List of (start_time, end_time) tuples.

    Returns:
        True if all events can be attended sequentially without overlap, False otherwise.

    Time Complexity: O(N log N) due to sorting.
    Space Complexity: O(N) to store the sorted copy (or O(1) auxiliary if sorted in-place).
    """
    # Validate all intervals first
    for s, e in events:
        if s > e:
            raise ValueError(f"Invalid event interval: start ({s}) cannot exceed end ({e}).")

    if len(events) <= 1:
        return True

    # Sort chronologically by start time
    sorted_events = sorted(events, key=lambda ev: ev[0])

    for i in range(1, len(sorted_events)):
        prev_start, prev_end = sorted_events[i - 1]
        curr_start, curr_end = sorted_events[i]

        # If current meeting starts strictly before previous meeting ends, overlap occurs
        if curr_start < prev_end:
            return False

    return True


def min_rooms_required(events: List[Event]) -> int:
    """
    Calculates the minimum number of meeting rooms required to accommodate all events.

    Uses a Min-Heap of meeting end times to greedily track room availability.

    Args:
        events: List of (start_time, end_time) tuples.

    Returns:
        Minimum integer count of rooms required.

    Time Complexity: O(N log N)
        - Sorting events: O(N log N)
        - N heap operations (push/pop): O(N log K), where K <= N is room count.
        - Overall: O(N log N)
    Space Complexity: O(N)
        - Storing sorted events: O(N)
        - Min-heap storing up to N end times: O(N)
    """
    if not events:
        return 0

    # Sort events chronologically by start time
    sorted_events = sorted(events, key=lambda ev: ev[0])

    # Min-heap to store end times of currently active rooms
    room_end_times: List[int] = []

    for start, end in sorted_events:
        if start > end:
            raise ValueError(f"Invalid event interval: ({start}, {end})")

        # If the earliest ending meeting has finished on or before current start time,
        # we can reuse that room.
        if room_end_times and room_end_times[0] <= start:
            heapq.heappop(room_end_times)

        # Allocate room (reused or newly opened) by tracking this event's end time
        heapq.heappush(room_end_times, end)

    # Size of the heap at the end equals the maximum concurrent rooms needed
    return len(room_end_times)


def min_rooms_required_sweep_line(events: List[Event]) -> int:
    """
    Alternative implementation using the Two-Pointer / Sweep-Line method.
    Sorts start and end times independently and simulates room occupancy over time.

    Time Complexity: O(N log N)
    Space Complexity: O(N)
    """
    if not events:
        return 0

    starts = sorted([e[0] for e in events])
    ends = sorted([e[1] for e in events])

    start_ptr = 0
    end_ptr = 0
    current_rooms = 0
    max_rooms = 0

    while start_ptr < len(events):
        # If the next event starts before the earliest event finishes, room is needed
        if starts[start_ptr] < ends[end_ptr]:
            current_rooms += 1
            max_rooms = max(max_rooms, current_rooms)
            start_ptr += 1
        else:
            # An event has concluded; a room is freed
            # (Note: starts[start_ptr] == ends[end_ptr] frees a room first because adjacent is allowed)
            current_rooms -= 1
            end_ptr += 1

    return max_rooms


if __name__ == "__main__":
    print("--- Event Scheduler Verification ---")
    test1 = [(9, 10), (10, 11), (11, 12)]
    print(f"Events: {test1}")
    print(f"can_attend_all: {can_attend_all(test1)} (expected True)")
    print(f"min_rooms_required (heap): {min_rooms_required(test1)} (expected 1)")
    print(f"min_rooms_required (sweep): {min_rooms_required_sweep_line(test1)} (expected 1)")

    test2 = [(9, 11), (10, 12), (11, 13)]
    print(f"\nEvents: {test2}")
    print(f"can_attend_all: {can_attend_all(test2)} (expected False)")
    print(f"min_rooms_required (heap): {min_rooms_required(test2)} (expected 2)")
    print(f"min_rooms_required (sweep): {min_rooms_required_sweep_line(test2)} (expected 2)")

    test3 = [(1, 4), (2, 5), (3, 6)]
    print(f"\nEvents: {test3}")
    print(f"min_rooms_required: {min_rooms_required(test3)} (expected 3)")
