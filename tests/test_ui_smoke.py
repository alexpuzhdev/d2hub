from __future__ import annotations

import pytest

from dota_hud.ui import get_hud_class


def test_qt_ui_import() -> None:
    pytest.importorskip("PySide6")
    hud_class = get_hud_class("qt")
    assert hud_class.__name__ == "HudQt"


def test_tk_ui_import() -> None:
    hud_class = get_hud_class("tk")
    assert hud_class.__name__ == "HudTk"
