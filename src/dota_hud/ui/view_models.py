from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HudViewModel:
    """Готовые тексты для отображения в HUD."""

    timer_text: str
    now_text: str
    next_text: str
    after_text: str
