from __future__ import annotations

import logging
from typing import Callable, Optional

from PySide6 import QtCore, QtGui, QtWidgets

logger = logging.getLogger(__name__)

DARK_STYLE = """
QWidget {
    background-color: #1a1f2e;
    color: #e5e7eb;
    font-size: 13px;
}
QTabWidget::pane {
    border: 1px solid #2a3040;
    background: #1a1f2e;
}
QTabBar::tab {
    background: #141820;
    color: #6b7280;
    padding: 8px 16px;
    border-bottom: 2px solid transparent;
}
QTabBar::tab:selected {
    color: #8b5cf6;
    border-bottom: 2px solid #8b5cf6;
}
QTableWidget {
    background: #1a1f2e;
    gridline-color: #2a3040;
    border: none;
}
QTableWidget::item {
    padding: 6px;
}
QHeaderView::section {
    background: #141820;
    color: #6b7280;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #2a3040;
}
QPushButton {
    background: #2a3040;
    color: #9ca3af;
    border: none;
    border-radius: 4px;
    padding: 6px 14px;
}
QPushButton:hover {
    background: #3a4050;
}
QPushButton#btn_add {
    background: #8b5cf6;
    color: white;
}
QPushButton#btn_save {
    background: #22c55e;
    color: white;
}
QPushButton#btn_delete {
    color: #ef4444;
}
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background: #141820;
    border: 1px solid #2a3040;
    border-radius: 4px;
    padding: 4px 8px;
    color: #e5e7eb;
}
"""


class AdminWindow(QtWidgets.QWidget):
    """Окно настроек D2Hub с вкладками."""

    config_changed = QtCore.Signal()

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("D2Hub — Настройки")
        self.setMinimumSize(700, 500)
        self.setStyleSheet(DARK_STYLE)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.addTab(self._build_timeline_tab(), "Тайминги")
        self.tabs.addTab(self._build_rules_tab(), "Правила")
        self.tabs.addTab(self._build_windows_tab(), "Предупреждения")
        self.tabs.addTab(self._build_macro_tab(), "Macro")
        self.tabs.addTab(self._build_build_tab(), "Сборка")
        self.tabs.addTab(self._build_settings_tab(), "Настройки")
        self.tabs.addTab(self._build_status_tab(), "Статус")

        layout.addWidget(self.tabs)

    def _build_toolbar(self) -> tuple[QtWidgets.QWidget, dict[str, QtWidgets.QPushButton]]:
        toolbar = QtWidgets.QWidget()
        toolbar_layout = QtWidgets.QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(12, 8, 12, 8)

        btn_add = QtWidgets.QPushButton("+ Добавить")
        btn_add.setObjectName("btn_add")
        btn_edit = QtWidgets.QPushButton("Изменить")
        btn_delete = QtWidgets.QPushButton("Удалить")
        btn_delete.setObjectName("btn_delete")
        btn_save = QtWidgets.QPushButton("Сохранить")
        btn_save.setObjectName("btn_save")

        toolbar_layout.addWidget(btn_add)
        toolbar_layout.addWidget(btn_edit)
        toolbar_layout.addWidget(btn_delete)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(btn_save)

        return toolbar, {"add": btn_add, "edit": btn_edit, "delete": btn_delete, "save": btn_save}

    def _build_timeline_tab(self) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        toolbar, self._timeline_buttons = self._build_toolbar()
        layout.addWidget(toolbar)

        self._timeline_buttons["add"].clicked.connect(lambda: self.add_timeline_row())
        self._timeline_buttons["delete"].clicked.connect(self.delete_selected_timeline_row)

        self.timeline_table = QtWidgets.QTableWidget(0, 3)
        self.timeline_table.setHorizontalHeaderLabels(["Время", "Подсказка", "Роли"])
        self.timeline_table.horizontalHeader().setStretchLastSection(True)
        self.timeline_table.setColumnWidth(0, 80)
        self.timeline_table.setColumnWidth(1, 350)
        self.timeline_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        layout.addWidget(self.timeline_table)

        return widget

    def _build_rules_tab(self) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        toolbar, self._rules_buttons = self._build_toolbar()
        layout.addWidget(toolbar)

        self.rules_table = QtWidgets.QTableWidget(0, 5)
        self.rules_table.setHorizontalHeaderLabels(["Старт", "До", "Каждые (сек)", "Текст", "Роли"])
        self.rules_table.horizontalHeader().setStretchLastSection(True)
        self.rules_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        layout.addWidget(self.rules_table)

        return widget

    def _build_windows_tab(self) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        toolbar, self._windows_buttons = self._build_toolbar()
        layout.addWidget(toolbar)

        self.windows_table = QtWidgets.QTableWidget(0, 5)
        self.windows_table.setHorizontalHeaderLabels(["От", "До", "Уровень", "Приоритет", "Текст"])
        self.windows_table.horizontalHeader().setStretchLastSection(True)
        self.windows_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        layout.addWidget(self.windows_table)

        return widget

    def _build_macro_tab(self) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        toolbar, self._macro_buttons = self._build_toolbar()
        layout.addWidget(toolbar)

        self.macro_table = QtWidgets.QTableWidget(0, 5)
        self.macro_table.setHorizontalHeaderLabels(["Название", "Спавн", "Интервал", "Окно", "Цвет"])
        self.macro_table.horizontalHeader().setStretchLastSection(True)
        self.macro_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        layout.addWidget(self.macro_table)

        return widget

    def _build_build_tab(self) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)

        self.build_hero_label = QtWidgets.QLabel("Герой: —")
        self.build_hero_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.build_hero_label)

        self.build_enabled_checkbox = QtWidgets.QCheckBox("Показывать подсказку в HUD")
        layout.addWidget(self.build_enabled_checkbox)

        self.build_items_label = QtWidgets.QLabel("Сборка: —")
        self.build_items_label.setWordWrap(True)
        layout.addWidget(self.build_items_label)

        layout.addStretch()
        return widget

    def _build_settings_tab(self) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.settings_x = QtWidgets.QSpinBox()
        self.settings_x.setRange(0, 9999)
        layout.addRow("Позиция X:", self.settings_x)

        self.settings_y = QtWidgets.QSpinBox()
        self.settings_y.setRange(0, 9999)
        layout.addRow("Позиция Y:", self.settings_y)

        self.settings_alpha = QtWidgets.QDoubleSpinBox()
        self.settings_alpha.setRange(0.1, 1.0)
        self.settings_alpha.setSingleStep(0.05)
        layout.addRow("Прозрачность:", self.settings_alpha)

        self.settings_font_size = QtWidgets.QSpinBox()
        self.settings_font_size.setRange(8, 48)
        layout.addRow("Размер шрифта:", self.settings_font_size)

        self.settings_lock_key = QtWidgets.QComboBox()
        self.settings_lock_key.addItems(["F7", "F8", "F9", "F10", "F11", "F12"])
        layout.addRow("Хоткей Lock:", self.settings_lock_key)

        self.settings_dota_path = QtWidgets.QLineEdit()
        browse_btn = QtWidgets.QPushButton("Обзор...")
        browse_btn.clicked.connect(self._browse_dota_path)
        dota_path_layout = QtWidgets.QHBoxLayout()
        dota_path_layout.addWidget(self.settings_dota_path)
        dota_path_layout.addWidget(browse_btn)
        layout.addRow("Путь к Dota:", dota_path_layout)

        return widget

    def _build_status_tab(self) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        self.status_dota = QtWidgets.QLabel("Dota 2: —")
        self.status_gsi = QtWidgets.QLabel("GSI: —")
        self.status_hero = QtWidgets.QLabel("Герой: —")
        self.status_role = QtWidgets.QLabel("Роль: —")
        self.status_config = QtWidgets.QLabel("Конфиг: —")

        for label in [self.status_dota, self.status_gsi, self.status_hero, self.status_role, self.status_config]:
            label.setStyleSheet("font-size: 14px; padding: 12px; background: #141820; border-radius: 8px;")
            layout.addWidget(label)

        btn_recreate = QtWidgets.QPushButton("Пересоздать GSI конфиг")
        btn_recreate.setObjectName("btn_add")
        btn_recreate.clicked.connect(self._handle_recreate_gsi)
        layout.addWidget(btn_recreate)

        layout.addStretch()
        return widget

    def _browse_dota_path(self) -> None:
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку Dota 2")
        if path:
            self.settings_dota_path.setText(path)

    def _handle_recreate_gsi(self) -> None:
        logger.info("Recreate GSI config requested")
        # Will be connected to actual logic in AppController

    def update_status(
        self,
        dota_running: bool = False,
        gsi_connected: bool = False,
        hero_name: str = "",
        role: str = "",
        config_valid: bool = True,
    ) -> None:
        """Обновляет вкладку статуса."""
        dot_green = "color: #22c55e;"
        dot_red = "color: #ef4444;"

        self.status_dota.setText(f"Dota 2: {'Запущена' if dota_running else 'Не найдена'}")
        self.status_dota.setStyleSheet(f"font-size: 14px; padding: 12px; background: #141820; border-radius: 8px; {dot_green if dota_running else dot_red}")

        self.status_gsi.setText(f"GSI: {'Подключён' if gsi_connected else 'Не подключён'}")
        self.status_gsi.setStyleSheet(f"font-size: 14px; padding: 12px; background: #141820; border-radius: 8px; {dot_green if gsi_connected else dot_red}")

        self.status_hero.setText(f"Герой: {hero_name or '—'}")
        self.status_role.setText(f"Роль: {role or '—'}")
        self.status_config.setText(f"Конфиг: {'Валиден' if config_valid else 'Ошибка'}")

    def load_timeline(self, data: list[dict]) -> None:
        """Загружает данные timeline в таблицу."""
        self.timeline_table.setRowCount(0)
        for entry in data:
            row = self.timeline_table.rowCount()
            self.timeline_table.insertRow(row)
            self.timeline_table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(entry.get("at", ""))))
            items = entry.get("items", [])
            self.timeline_table.setItem(row, 1, QtWidgets.QTableWidgetItem(", ".join(items) if isinstance(items, list) else str(items)))
            roles = entry.get("roles", [])
            self.timeline_table.setItem(row, 2, QtWidgets.QTableWidgetItem(", ".join(roles) if roles else "все"))

    def export_timeline(self) -> list[dict]:
        """Экспортирует данные timeline из таблицы."""
        result = []
        for row in range(self.timeline_table.rowCount()):
            at = self.timeline_table.item(row, 0)
            items_text = self.timeline_table.item(row, 1)
            roles_text = self.timeline_table.item(row, 2)

            at_val = at.text() if at else ""
            items_val = [s.strip() for s in items_text.text().split(",") if s.strip()] if items_text else []
            roles_raw = roles_text.text() if roles_text else ""
            roles_val = [s.strip() for s in roles_raw.split(",") if s.strip() and s.strip() != "все"] if roles_raw else []

            result.append({"at": at_val, "items": items_val, "roles": roles_val})
        return result

    def add_timeline_row(self, at: str = "", items: str = "", roles: str = "все") -> None:
        """Добавляет строку в таблицу timeline."""
        row = self.timeline_table.rowCount()
        self.timeline_table.insertRow(row)
        self.timeline_table.setItem(row, 0, QtWidgets.QTableWidgetItem(at))
        self.timeline_table.setItem(row, 1, QtWidgets.QTableWidgetItem(items))
        self.timeline_table.setItem(row, 2, QtWidgets.QTableWidgetItem(roles))

    def delete_selected_timeline_row(self) -> None:
        """Удаляет выбранную строку из timeline."""
        rows = set(index.row() for index in self.timeline_table.selectedIndexes())
        for row in sorted(rows, reverse=True):
            self.timeline_table.removeRow(row)
