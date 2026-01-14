from __future__ import annotations

import importlib.util
import logging

from .base import HudBase
from .hud_style import HudStyle

logger = logging.getLogger(__name__)


def create_hud(style: HudStyle, ui_type: str, *, allow_tk_fallback: bool = False) -> HudBase:
    normalized = (ui_type or "tk").strip().lower()
    logger.info("UI backend selected: %s", normalized or "tk")

    if normalized in {"qt", "pyside6", "pyside"}:
        if importlib.util.find_spec("PySide6") is None:
            message = (
                "PySide6 backend requested but PySide6 is not available. "
                "Install PySide6 or switch ui.backend to 'tk'."
            )
            if allow_tk_fallback:
                logger.warning("%s Falling back to Tkinter.", message)
                from .tk.hud_window import HudTk

                hud = HudTk(style)
                logger.info("UI backend: Tkinter")
                return hud
            raise RuntimeError(message)

        from .qt.hud_window import HudQt

        hud = HudQt(style)
        logger.info("UI backend: PySide6")
        return hud

    if normalized in {"tk", "tkinter"}:
        from .tk.hud_window import HudTk

        hud = HudTk(style)
        logger.info("UI backend: Tkinter")
        return hud

    raise ValueError(f"Unknown UI backend '{ui_type}'. Use 'qt' or 'tk'.")
