from __future__ import annotations

from dataclasses import dataclass

from .events import format_mmss


@dataclass(frozen=True)
class MacroTiming:
    """Описание базового макро-тайминга."""

    name: str
    first_spawn: int
    interval: int
    up_window: int
    color: str | None = None

    def status(self, elapsed: int) -> str:
        """Возвращает строковый статус для HUD."""
        if elapsed < self.first_spawn:
            return format_mmss(self.first_spawn - elapsed)
        if self.interval <= 0:
            return "UP"
        since_last = (elapsed - self.first_spawn) % self.interval
        if since_last <= self.up_window:
            return "UP"
        return format_mmss(self.interval - since_last)

    def progress(self, elapsed: int) -> float:
        """Возвращает прогресс до следующего спавна (0..1)."""
        if elapsed < self.first_spawn:
            return max(0.0, min(1.0, elapsed / self.first_spawn)) if self.first_spawn else 1.0
        if self.interval <= 0:
            return 1.0
        since_last = (elapsed - self.first_spawn) % self.interval
        return max(0.0, min(1.0, since_last / self.interval))


DEFAULT_MACRO_TIMINGS: tuple[MacroTiming, ...] = (
    MacroTiming(
        name="Wisdom rune",
        first_spawn=7 * 60,
        interval=7 * 60,
        up_window=30,
        color="#8b5cf6",
    ),
    MacroTiming(
        name="Power rune",
        first_spawn=6 * 60,
        interval=2 * 60,
        up_window=30,
        color="#3b82f6",
    ),
    MacroTiming(
        name="Bounty rune",
        first_spawn=0,
        interval=3 * 60,
        up_window=30,
        color="#f59e0b",
    ),
)


def build_macro_lines(
    elapsed: int,
    timings: tuple[MacroTiming, ...] | list[MacroTiming] | None = None,
) -> list[str]:
    """Собирает строки с базовой макро-информацией."""
    source = timings if timings is not None else DEFAULT_MACRO_TIMINGS
    return [f"{timing.name}: {timing.status(elapsed)}" for timing in source]
