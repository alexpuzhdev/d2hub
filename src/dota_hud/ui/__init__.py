from __future__ import annotations

from typing import Any

from .hud_style import HudStyle


def create_hud(style: HudStyle, ui_type: str) -> Any:
    normalized = (ui_type or "tk").strip().lower()
    if normalized in {"qt", "pyside6", "pyside"}:
        try:
            from .qt.hud_window import HudQt
        except ImportError:
            normalized = "tk"
        else:
            return HudQt(style)

    from .hud_tk import HudTk

    return HudTk(style)
