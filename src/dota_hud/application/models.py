from __future__ import annotations

from dataclasses import dataclass


__all__ = ["WarningState", "HudState", "GameStateSnapshot"]


@dataclass(frozen=True)
class WarningState:
    """Состояние предупреждения для отображения."""

    text: str | None
    level: str | None


@dataclass(frozen=True)
class HudState:
    """Состояние HUD для передачи в слой представления."""

    timer_text: str
    now_text: str
    now_level: str | None
    next_text: str
    next_level: str | None
    macro_text: str
    macro_level: str | None
    warning: WarningState


@dataclass(frozen=True)
class GameStateSnapshot:
    """Минимальный снимок состояния игры для use-case."""

    clock_time: int | None
    paused: bool
