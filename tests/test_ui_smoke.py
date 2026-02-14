from __future__ import annotations

import importlib

import pytest


def test_qt_ui_import() -> None:
    pytest.importorskip("PySide6")
    try:
        module = importlib.import_module("dota_hud.ui.qt.hud_window")
    except ImportError as exc:
        pytest.skip(f"Qt deps not available: {exc}")
    assert hasattr(module, "HudQt")
