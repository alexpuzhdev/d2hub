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
        self._external_elapsed: Optional[int] = None
        self.reset()

    # ---------- РУЧНОЙ РЕЖИМ ----------
    def start(self) -> None:
        self._external_elapsed = None
        self._start_at = time.time()
        self._buckets = list(self._base)

    def stop(self) -> None:
        self._start_at = None

    def reset(self) -> None:
        self._start_at = None
        self._external_elapsed = None
        self._buckets = list(self._base)

    @property
    def is_running(self) -> bool:
        return self._start_at is not None or self._external_elapsed is not None

    # ---------- GSI РЕЖИМ ----------
    def set_external_elapsed(self, seconds: int) -> None:
        """
        Устанавливает текущее игровое время извне (GSI).
        """
        if self._external_elapsed is None:
            # первый апдейт — пересобираем бакеты
            self._buckets = list(self._base)
        self._external_elapsed = max(0, int(seconds))
        self._start_at = None

    def clear_external(self) -> None:
        self._external_elapsed = None

    # ---------- ОБЩАЯ ЛОГИКА ----------
    def elapsed(self) -> int:
        if self._external_elapsed is not None:
            return self._external_elapsed
        return 0 if self._start_at is None else int(time.time() - self._start_at)

    def tick(self) -> TickState:
        elapsed = self.elapsed()

        if elapsed == 0 and not self.is_running:
            nxt = self._buckets[0] if self._buckets else None
            aft = self._buckets[1] if len(self._buckets) > 1 else None
            return TickState(0, None, nxt, aft)

        now = None
        while self._buckets and self._buckets[0].t <= elapsed:
            now = self._buckets.pop(0)

        nxt = self._buckets[0] if self._buckets else None
        aft = self._buckets[1] if len(self._buckets) > 1 else None

        return TickState(elapsed, now, nxt, aft)
