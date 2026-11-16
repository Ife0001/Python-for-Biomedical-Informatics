"""Iterative three-way quicksort implementations for integer datasets."""
from __future__ import annotations

import random
from typing import MutableSequence


def quicksort(values: MutableSequence[int], *, pivot: str = "first", seed: int = 42) -> None:
    """Sort *values* in place using three-way partitioning and an explicit stack.

    pivot may be 'first' or 'random'. Random pivot selection is seeded for
    reproducibility; it is not a cryptographic RNG.
    """
    if pivot not in {"first", "random"}:
        raise ValueError("pivot must be 'first' or 'random'")
    generator = random.Random(seed)
    if len(values) < 2:
        return
    stack = [(0, len(values) - 1)]
    while stack:
        lo, hi = stack.pop()
        while lo < hi:
            pivot_i = lo if pivot == "first" else generator.randint(lo, hi)
            pivot_value = values[pivot_i]
            # Dutch national flag partition: [lo, lt) < pivot;
            # [lt, gt] == pivot; (gt, hi] > pivot.
            lt, i, gt = lo, lo, hi
            while i <= gt:
                if values[i] < pivot_value:
                    values[lt], values[i] = values[i], values[lt]
                    lt += 1
                    i += 1
                elif values[i] > pivot_value:
                    values[i], values[gt] = values[gt], values[i]
                    gt -= 1
                else:
                    i += 1
            # Process shorter side inline, push longer side to bound stack use.
            left_size, right_size = lt - lo, hi - gt
            if left_size < right_size:
                if gt + 1 < hi:
                    stack.append((gt + 1, hi))
                hi = lt - 1
            else:
                if lo < lt - 1:
                    stack.append((lo, lt - 1))
                lo = gt + 1


def make_dataset(kind: str, size: int, *, seed: int = 42) -> list[int]:
    """Return deterministic arrays, including duplicates and adverse orderings."""
    if size < 0:
        raise ValueError("size must be nonnegative")
    rng = random.Random(seed)
    if kind == "random":
        return [rng.randint(0, max(10, size // 4)) for _ in range(size)]
    if kind == "sorted":
        return list(range(size))
    if kind == "reversed":
        return list(range(size - 1, -1, -1))
    if kind == "identical":
        return [17] * size
    raise ValueError(f"unknown dataset type: {kind}")
