from __future__ import annotations

from typing import Any, Type

from .hud_style import HudStyle


def get_hud_class(ui_type: str) -> Type[Any]:
    normalized = (ui_type or "tk").strip().lower()
    if normalized in {"qt", "pyside6", "pyside"}:
        try:
            from .qt.hud_window import HudQt
        except ImportError as exc:
            raise RuntimeError(
                "PySide6 UI backend requested but PySide6 is not installed."
            ) from exc
        return HudQt
    if normalized in {"tk", "tkinter"}:
        from .hud_tk import HudTk

        return HudTk
    raise ValueError(f"Unknown UI backend: {ui_type}")


def create_hud(style: HudStyle, ui_type: str) -> Any:
    hud_class = get_hud_class(ui_type)
    return hud_class(style)
