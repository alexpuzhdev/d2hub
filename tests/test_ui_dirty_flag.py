"""Tests for HudQt dirty-flag optimisation.

The dirty flag prevents redundant Qt repaints when set_now / set_next /
set_timer are called with unchanged data every 200 ms.
"""

from __future__ import annotations

import importlib
import sys

import pytest


def _make_hud():
    """Create a minimal HudQt instance, skipping if Qt is unavailable."""
    PySide6 = pytest.importorskip("PySide6")  # noqa: N806
    try:
        module = importlib.import_module("dota_hud.ui.qt.hud_window")
    except ImportError as exc:
        pytest.skip(f"Qt deps not available: {exc}")

    from dota_hud.ui.hud_style import HudStyle

    style = HudStyle(
        title="test",
        width=300,
        height=100,
        x=0,
        y=0,
        alpha=1.0,
        font_family="sans-serif",
        font_size=12,
        font_weight="normal",
        margin_horizontal=4,
        margin_vertical=4,
        spacing=2,
        block_padding=4,
        text_fade_duration_ms=0,
        text_fade_start_opacity=1.0,
        macro_line_spacing=2,
        macro_bar_height=16,
        macro_show_title=False,
    )
    hud = module.HudQt(style)
    return hud


# ---- set_now tests ----------------------------------------------------------

class TestSetNowDirtyFlag:
    def test_same_text_and_level_does_not_set_dirty(self) -> None:
        hud = _make_hud()
        hud.set_now("hello", "info")
        hud._dirty = False  # reset after first call

        hud.set_now("hello", "info")
        assert hud._dirty is False

    def test_different_text_sets_dirty(self) -> None:
        hud = _make_hud()
        hud.set_now("hello", "info")
        hud._dirty = False

        hud.set_now("world", "info")
        assert hud._dirty is True

    def test_different_level_sets_dirty(self) -> None:
        hud = _make_hud()
        hud.set_now("hello", "info")
        hud._dirty = False

        hud.set_now("hello", "warn")
        assert hud._dirty is True

    def test_none_level_normalised(self) -> None:
        hud = _make_hud()
        hud.set_now("hello")  # level=None -> ""
        hud._dirty = False

        hud.set_now("hello", None)
        assert hud._dirty is False


# ---- set_next tests ---------------------------------------------------------

class TestSetNextDirtyFlag:
    def test_same_text_and_level_does_not_set_dirty(self) -> None:
        hud = _make_hud()
        hud.set_next("hello", "info")
        hud._dirty = False

        hud.set_next("hello", "info")
        assert hud._dirty is False

    def test_different_text_sets_dirty(self) -> None:
        hud = _make_hud()
        hud.set_next("hello", "info")
        hud._dirty = False

        hud.set_next("world", "info")
        assert hud._dirty is True

    def test_different_level_sets_dirty(self) -> None:
        hud = _make_hud()
        hud.set_next("hello", "info")
        hud._dirty = False

        hud.set_next("hello", "danger")
        assert hud._dirty is True


# ---- set_timer tests --------------------------------------------------------

class TestSetTimerDirtyFlag:
    def test_same_text_does_not_set_dirty(self) -> None:
        hud = _make_hud()
        hud.set_timer("1:30")
        hud._dirty = False

        hud.set_timer("1:30")
        assert hud._dirty is False

    def test_different_text_sets_dirty(self) -> None:
        hud = _make_hud()
        hud.set_timer("1:30")
        hud._dirty = False

        hud.set_timer("1:31")
        assert hud._dirty is True
