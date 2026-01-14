from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WarningWindow:
    """Описание окна предупреждения."""

    from_t: int
    to_t: int
    text: str
    level: str = "info"
    priority: int = 0


class WarningWindowService:
    """Определяет активные предупреждения по времени."""

    def active_windows(self, elapsed: int, windows: list[WarningWindow]) -> list[WarningWindow]:
        """Возвращает список активных окон предупреждений."""
        active = [
            (index, window)
            for index, window in enumerate(windows)
            if window.from_t <= elapsed <= window.to_t
        ]
        active.sort(key=lambda item: (-item[1].priority, item[1].from_t, item[0]))
        return [window for _, window in active]

    def warning_level(self, active_windows: list[WarningWindow]) -> str:
        """Возвращает уровень предупреждения по активным окнам."""
        for level in ("danger", "warn", "info"):
            if any(window.level == level for window in active_windows):
                return level
        return ""
