from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HudStyle:
    """Настройки внешнего вида HUD."""

    title: str
    width: int
    height: int
    x: int
    y: int
    alpha: float
    font_family: str
    font_size: int
    font_weight: str
    margin_horizontal: int
    margin_vertical: int
    spacing: int
    block_padding: int
    text_fade_duration_ms: int
    text_fade_start_opacity: float
