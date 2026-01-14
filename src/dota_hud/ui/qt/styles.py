from __future__ import annotations

from dataclasses import dataclass

from PySide6 import QtGui


@dataclass(frozen=True)
class HudColors:
    background_normal: QtGui.QColor
    background_warn: QtGui.QColor
    text_primary: QtGui.QColor
    text_muted: QtGui.QColor


def default_colors() -> HudColors:
    return HudColors(
        background_normal=QtGui.QColor(11, 11, 11),
        background_warn=QtGui.QColor(32, 16, 0),
        text_primary=QtGui.QColor(255, 255, 255),
        text_muted=QtGui.QColor(189, 189, 189),
    )
