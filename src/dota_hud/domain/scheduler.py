from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional

from .events import Bucket


@dataclass
class TickState:
    """Снимок состояния таймеров на текущем тике."""

    elapsed: int
    now: Optional[Bucket]
    next_event: Optional[Bucket]
    after_event: Optional[Bucket]


class Scheduler:
    """Планировщик игровых событий, учитывающий ручной и внешний таймеры."""

    def __init__(self, buckets: list[Bucket]) -> None:
        """Создаёт планировщик с базовым списком событий."""
        self._base = list(buckets)
        self._external_elapsed: Optional[int] = None
        self.reset()

    def start(self) -> None:
        """Запускает ручной таймер."""
        self._external_elapsed = None
        self._start_at = time.time()
        self._buckets = list(self._base)

    def stop(self) -> None:
        """Останавливает ручной таймер."""
        self._start_at = None

    def reset(self) -> None:
        """Сбрасывает таймер и события."""
        self._start_at = None
        self._external_elapsed = None
        self._buckets = list(self._base)

    @property
    def is_running(self) -> bool:
        """Возвращает признак активности таймера."""
        return self._start_at is not None or self._external_elapsed is not None

    def set_external_elapsed(self, seconds: int) -> None:
        """Устанавливает текущее игровое время извне (GSI)."""
        if self._external_elapsed is None:
            self._buckets = list(self._base)
        self._external_elapsed = max(0, int(seconds))
        self._start_at = None

    def clear_external(self) -> None:
        """Сбрасывает внешний источник времени."""
        self._external_elapsed = None

    def elapsed(self) -> int:
        """Возвращает прошедшее время в секундах."""
        if self._external_elapsed is not None:
            return self._external_elapsed
        return 0 if self._start_at is None else int(time.time() - self._start_at)

    def tick(self) -> TickState:
        """Вычисляет новое состояние таймингов."""
        elapsed = self.elapsed()

        if elapsed == 0 and not self.is_running:
            next_event = self._buckets[0] if self._buckets else None
            after_event = self._buckets[1] if len(self._buckets) > 1 else None
            return TickState(0, None, next_event, after_event)

        now = None
        while self._buckets and self._buckets[0].t <= elapsed:
            now = self._buckets.pop(0)

        next_event = self._buckets[0] if self._buckets else None
        after_event = self._buckets[1] if len(self._buckets) > 1 else None

        return TickState(elapsed, now, next_event, after_event)
