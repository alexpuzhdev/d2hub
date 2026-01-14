from __future__ import annotations

from dataclasses import dataclass


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
    next_text: str
    after_text: str
    warning: WarningState
