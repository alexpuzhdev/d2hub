"""Tests for HudQt skip-on-unchanged optimisation.

Verifies that set_now / set_next / set_timer skip calling setText
when invoked with unchanged data.
"""

from __future__ import annotations

import importlib
from unittest.mock import patch

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

class TestSetNowSkipBehavior:
    def test_same_text_and_level_skips_setText(self) -> None:
        hud = _make_hud()
        hud.set_now("hello", "info")
        with patch.object(hud.now, "setText") as mock_set:
            hud.set_now("hello", "info")
            mock_set.assert_not_called()

    def test_different_text_calls_setText(self) -> None:
        hud = _make_hud()
        hud.set_now("hello", "info")
        with patch.object(hud.now, "setText") as mock_set:
            hud.set_now("world", "info")
            mock_set.assert_called_once_with("world")

    def test_different_level_calls_setText(self) -> None:
        hud = _make_hud()
        hud.set_now("hello", "info")
        with patch.object(hud.now, "setText") as mock_set:
            hud.set_now("hello", "warn")
            mock_set.assert_called_once_with("hello")

    def test_none_level_normalised(self) -> None:
        hud = _make_hud()
        hud.set_now("hello")  # level=None -> ""
        with patch.object(hud.now, "setText") as mock_set:
            hud.set_now("hello", None)
            mock_set.assert_not_called()


# ---- set_next tests ---------------------------------------------------------

class TestSetNextSkipBehavior:
    def test_same_text_and_level_skips_setText(self) -> None:
        hud = _make_hud()
        hud.set_next("hello", "info")
        with patch.object(hud.next, "setText") as mock_set:
            hud.set_next("hello", "info")
            mock_set.assert_not_called()

    def test_different_text_calls_setText(self) -> None:
        hud = _make_hud()
        hud.set_next("hello", "info")
        with patch.object(hud.next, "setText") as mock_set:
            hud.set_next("world", "info")
            mock_set.assert_called_once_with("world")

    def test_different_level_calls_setText(self) -> None:
        hud = _make_hud()
        hud.set_next("hello", "info")
        with patch.object(hud.next, "setText") as mock_set:
            hud.set_next("hello", "danger")
            mock_set.assert_called_once_with("hello")


# ---- set_timer tests --------------------------------------------------------

class TestSetTimerSkipBehavior:
    def test_same_text_skips_setText(self) -> None:
        hud = _make_hud()
        hud.set_timer("1:30")
        with patch.object(hud.timer, "setText") as mock_set:
            hud.set_timer("1:30")
            mock_set.assert_not_called()

    def test_different_text_calls_setText(self) -> None:
        hud = _make_hud()
        hud.set_timer("1:30")
        with patch.object(hud.timer, "setText") as mock_set:
            hud.set_timer("1:31")
            mock_set.assert_called_once_with("1:31")
