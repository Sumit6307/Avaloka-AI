"""
Problem 1: Least Recently Used (LRU) Cache Implementation
==========================================================

Problem Statement:
Design and implement a data structure for a Least Recently Used (LRU) cache.
It should support the following operations in O(1) time complexity:
- get(key): Returns the value of key if it exists, otherwise -1. Marks key as most recently used.
- put(key, value): Updates value if key exists, or inserts key-value pair. If size exceeds capacity,
  evicts the least recently used item.

Data Structure Selection Explanation:
-------------------------------------
To achieve O(1) time complexity for both `get` and `put` operations, we combine two data structures:
1. Hash Map (Dictionary in Python):
   - Maps each `key` to its corresponding `Node` reference in memory.
   - Provides O(1) average-time lookup to find any node given its key.
2. Doubly Linked List (DLL):
   - Maintains the recency ordering of keys.
   - Each node contains `key`, `value`, `prev`, and `next` pointers.
   - We utilize two sentinel (dummy) nodes: `head` (most recently used side) and `tail` (least recently used side).
   - Sentinel nodes eliminate boundary checks (e.g., updating head/tail when list is empty or has 1 node).
   - Given a pointer to any node in a doubly linked list, we can remove it in O(1) time by re-linking its
     neighbors (`node.prev.next = node.next` and `node.next.prev = node.prev`). In contrast, a singly
     linked list would require O(N) traversal to locate the preceding node.
   - Inserting a node immediately after `head` (marking as most recently used) is strictly O(1).
   - Evicting the least recently used item is strictly O(1) by accessing `tail.prev`.

Combined Workflow:
- `get(key)`: Lookup node via Hash Map in O(1). If not found, return -1.
  If found, remove the node from its current DLL position and insert right after `head`. Return `node.val`.
- `put(key, value)`:
  - If `key` already exists: update `node.val`, move node to after `head`.
  - If `key` is new:
    - If current size reaches `capacity`, identify LRU node via `tail.prev`, remove it from DLL,
      and delete its key from the Hash Map (in O(1)).
    - Create a new node, insert it after `head`, and add entry to Hash Map (in O(1)).
"""

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
    LRU Cache supporting get and put operations in O(1) time.

    Attributes:
        capacity (int): Maximum number of items the cache can hold.
        map (dict): Maps key to Node reference.
        head (Node): Dummy head sentinel (MRU end is head.next).
        tail (Node): Dummy tail sentinel (LRU end is tail.prev).
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
        """Removes an existing node from the doubly linked list in O(1)."""
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
        """Removes and returns the least recently used node (tail.prev) in O(1)."""
        lru_node = self.tail.prev
        assert lru_node is not None and lru_node is not self.head, "Cannot pop from empty list"
        self._remove(lru_node)
        return lru_node

    def get(self, key: Any) -> Any:
        """
        Retrieves the value for key if present, marking it as most recently used.
        Returns -1 if key is not found.
        Time Complexity: O(1)
        """
        if key not in self.map:
            return -1

        node = self.map[key]
        self._move_to_head(node)
        return node.val

    def put(self, key: Any, value: Any) -> None:
        """
        Adds or updates key-value pair. Evicts the LRU item if capacity is reached.
        Time Complexity: O(1)
        """
        if key in self.map:
            # Update existing key
            node = self.map[key]
            node.val = value
            self._move_to_head(node)
        else:
            # Check capacity before inserting new key
            if len(self.map) >= self.capacity:
                lru_node = self._pop_tail()
                del self.map[lru_node.key]

            # Insert new key at MRU
            new_node = Node(key, value)
            self.map[key] = new_node
            self._add_to_head(new_node)

    def __len__(self) -> int:
        """Returns the current number of items stored in cache."""
        return len(self.map)

    def get_order_keys(self) -> list[Any]:
        """Utility for inspection: returns keys from Most Recently Used to Least Recently Used."""
        keys = []
        curr = self.head.next
        while curr is not None and curr is not self.tail:
            keys.append(curr.key)
            curr = curr.next
        return keys


if __name__ == "__main__":
    print("--- LRU Cache Verification ---")
    cache = LRUCache(2)
    cache.put(1, 100)
    cache.put(2, 200)
    print(f"get(1): {cache.get(1)} (expected 100)")
    cache.put(3, 300)  # Evicts key 2
    print(f"get(2): {cache.get(2)} (expected -1, evicted)")
    cache.put(4, 400)  # Evicts key 1
    print(f"get(1): {cache.get(1)} (expected -1, evicted)")
    print(f"get(3): {cache.get(3)} (expected 300)")
    print(f"get(4): {cache.get(4)} (expected 400)")
    print("Recency order (MRU -> LRU):", cache.get_order_keys())
