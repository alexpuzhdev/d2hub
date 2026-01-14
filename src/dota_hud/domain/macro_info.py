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

    def status(self, elapsed: int) -> str:
        """Возвращает строковый статус для HUD."""
        if elapsed < self.first_spawn:
            return format_mmss(self.first_spawn - elapsed)
        if self.interval <= 0:
            return "ГОТОВО"
        since_last = (elapsed - self.first_spawn) % self.interval
        if since_last <= self.up_window:
            return "ГОТОВО"
        return format_mmss(self.interval - since_last)


DEFAULT_MACRO_TIMINGS: tuple[MacroTiming, ...] = (
    MacroTiming(name="Руна мудрости", first_spawn=7 * 60, interval=7 * 60, up_window=30),
    MacroTiming(name="Активная руна", first_spawn=6 * 60, interval=2 * 60, up_window=30),
    MacroTiming(name="Руна богатства", first_spawn=0, interval=3 * 60, up_window=30),
)


def build_macro_lines(elapsed: int) -> list[str]:
    """Собирает строки с базовой макро-информацией."""
    return [f"{timing.name}: {timing.status(elapsed)}" for timing in DEFAULT_MACRO_TIMINGS]
