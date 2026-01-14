from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HudStyle:
    title: str
    width: int
    height: int
    x: int
    y: int
    alpha: float
    font_family: str
    font_size: int
    font_weight: str
