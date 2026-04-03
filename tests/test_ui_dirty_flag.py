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


# ---- MacroProgressBar widget pool tests ------------------------------------

def _make_macro_lines(count: int):
    """Create a list of MacroLine instances for testing."""
    from dota_hud.application.models import MacroLine

    return [
        MacroLine(text=f"line-{i}", progress=i * 0.1, color=None)
        for i in range(count)
    ]


class TestMacroLineWidgetPool:
    def test_same_count_reuses_widgets(self) -> None:
        """When line count stays the same, widget objects are reused."""
        hud = _make_hud()
        lines_a = _make_macro_lines(3)
        hud._apply_macro_lines(lines_a)
        widgets_before = list(hud._macro_line_widgets)

        lines_b = _make_macro_lines(3)
        hud._apply_macro_lines(lines_b)
        widgets_after = list(hud._macro_line_widgets)

        assert len(widgets_before) == 3
        assert len(widgets_after) == 3
        for before, after in zip(widgets_before, widgets_after):
            assert before is after, "Widget should be reused, not recreated"

    def test_shrink_removes_excess(self) -> None:
        """Going from 3 lines to 2 should remove 1 widget."""
        hud = _make_hud()
        hud._apply_macro_lines(_make_macro_lines(3))
        assert len(hud._macro_line_widgets) == 3
        kept = list(hud._macro_line_widgets[:2])

        hud._apply_macro_lines(_make_macro_lines(2))
        assert len(hud._macro_line_widgets) == 2
        for before, after in zip(kept, hud._macro_line_widgets):
            assert before is after, "Surviving widgets should be reused"

    def test_grow_adds_new(self) -> None:
        """Going from 2 lines to 3 should add 1 widget, keeping existing."""
        hud = _make_hud()
        hud._apply_macro_lines(_make_macro_lines(2))
        assert len(hud._macro_line_widgets) == 2
        kept = list(hud._macro_line_widgets)

        hud._apply_macro_lines(_make_macro_lines(3))
        assert len(hud._macro_line_widgets) == 3
        for before, after in zip(kept, hud._macro_line_widgets[:2]):
            assert before is after, "Existing widgets should be reused"

    def test_empty_lines_show_fallback(self) -> None:
        """Empty lines list should show a single fallback QLabel."""
        PySide6 = pytest.importorskip("PySide6")  # noqa: N806
        from PySide6 import QtWidgets

        hud = _make_hud()
        hud._apply_macro_lines(_make_macro_lines(3))
        hud._apply_macro_lines([])
        assert len(hud._macro_line_widgets) == 1
        assert isinstance(hud._macro_line_widgets[0], QtWidgets.QLabel)

    def test_fallback_to_lines_replaces_label(self) -> None:
        """Going from fallback to real lines should replace the QLabel."""
        hud = _make_hud()
        hud._apply_macro_lines([])
        assert len(hud._macro_line_widgets) == 1

        hud._apply_macro_lines(_make_macro_lines(2))
        assert len(hud._macro_line_widgets) == 2
