from __future__ import annotations

import pytest

PySide6 = pytest.importorskip("PySide6")

from dota_hud.ui.qt.tray import ROLE_LABELS, TrayIcon, TrayState  # noqa: E402


def test_tray_state_enum() -> None:
    assert TrayState.WAITING.value == "waiting"
    assert TrayState.DOTA_FOUND.value == "dota_found"
    assert TrayState.GSI_ACTIVE.value == "gsi_active"


def test_role_labels_dict() -> None:
    assert "carry" in ROLE_LABELS
    assert "mid" in ROLE_LABELS
    assert "offlane" in ROLE_LABELS
    assert "soft_support" in ROLE_LABELS
    assert "hard_support" in ROLE_LABELS
    assert len(ROLE_LABELS) == 5


@pytest.mark.usefixtures()
def test_tray_instantiation(qtbot) -> None:  # type: ignore[no-untyped-def]
    tray = TrayIcon()
    assert tray.state == TrayState.WAITING
