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
        active = [window for window in windows if window.from_t <= elapsed <= window.to_t]
        active.sort(key=lambda window: window.priority, reverse=True)
        return active

    def warning_level(self, active_windows: list[WarningWindow]) -> str:
        """Возвращает уровень предупреждения по активным окнам."""
        for level in ("danger", "warn", "info"):
            if any(window.level == level for window in active_windows):
                return level
        return ""
