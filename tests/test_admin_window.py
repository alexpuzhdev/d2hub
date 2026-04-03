from __future__ import annotations
import pytest

pytest.importorskip("PySide6")

from dota_hud.ui.qt.admin_window import AdminWindow


def test_admin_window_has_tabs(qtbot):
    admin = AdminWindow()
    qtbot.addWidget(admin)
    tab_names = [admin.tabs.tabText(i) for i in range(admin.tabs.count())]
    assert "Тайминги" in tab_names
    assert "Правила" in tab_names
    assert "Предупреждения" in tab_names
    assert "Macro" in tab_names
    assert "Сборка" in tab_names
    assert "Настройки" in tab_names
    assert "Статус" in tab_names


def test_load_timeline_data(qtbot):
    admin = AdminWindow()
    qtbot.addWidget(admin)
    data = [
        {"at": "0:00", "items": ["Buy wards"], "roles": ["hard_support"]},
        {"at": "7:00", "items": ["Wisdom rune"], "roles": []},
    ]
    admin.load_timeline(data)
    assert admin.timeline_table.rowCount() == 2
    assert admin.timeline_table.item(0, 0).text() == "0:00"
    assert admin.timeline_table.item(0, 1).text() == "Buy wards"


def test_export_timeline_data(qtbot):
    admin = AdminWindow()
    qtbot.addWidget(admin)
    data = [
        {"at": "0:00", "items": ["Buy wards"], "roles": ["hard_support"]},
    ]
    admin.load_timeline(data)
    exported = admin.export_timeline()
    assert len(exported) == 1
    assert exported[0]["at"] == "0:00"
    assert exported[0]["items"] == ["Buy wards"]
    assert exported[0]["roles"] == ["hard_support"]
