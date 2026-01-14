from __future__ import annotations

import importlib

import pytest


def test_qt_ui_import() -> None:
    pytest.importorskip("PySide6")
    module = importlib.import_module("dota_hud.ui.qt.hud_window")
    assert hasattr(module, "HudQt")
