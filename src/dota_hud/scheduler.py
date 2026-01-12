from __future__ import annotations
import time
from dataclasses import dataclass
from typing import List, Optional

from .events import Bucket

@dataclass
class TickState:
    elapsed: int
    now: Optional[Bucket]
    next_: Optional[Bucket]
    after: Optional[Bucket]

class Scheduler:
    def __init__(self, buckets: List[Bucket]) -> None:
        self._base = list(buckets)
        self.reset()

    def start(self) -> None:
        self._start_at = time.time()
        self._buckets = list(self._base)

    def stop(self) -> None:
        self._start_at = None

    def reset(self) -> None:
        self._start_at = None
        self._buckets = list(self._base)

    @property
    def is_running(self) -> bool:
        return self._start_at is not None

    def elapsed(self) -> int:
        return 0 if self._start_at is None else int(time.time() - self._start_at)

    def tick(self) -> TickState:
        if self._start_at is None:
            nxt = self._buckets[0] if self._buckets else None
            aft = self._buckets[1] if len(self._buckets) > 1 else None
            return TickState(0, None, nxt, aft)

        elapsed = self.elapsed()

        now = None
        if self._buckets and self._buckets[0].t == elapsed:
            now = self._buckets.pop(0)

        nxt = self._buckets[0] if self._buckets else None
        aft = self._buckets[1] if len(self._buckets) > 1 else None
        return TickState(elapsed, now, nxt, aft)
