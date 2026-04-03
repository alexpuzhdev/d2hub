from __future__ import annotations

import logging
from enum import Enum
from typing import Callable, Optional

from PySide6 import QtCore, QtGui, QtWidgets

logger = logging.getLogger(__name__)


class TrayState(Enum):
    WAITING = "waiting"
    DOTA_FOUND = "dota_found"
    GSI_ACTIVE = "gsi_active"


ROLE_LABELS = {
    "carry": "Carry",
    "mid": "Mid",
    "offlane": "Offlane",
    "soft_support": "Soft Support",
    "hard_support": "Hard Support",
}


class TrayIcon(QtWidgets.QSystemTrayIcon):
    """Иконка в системном трее с контекстным меню."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self._state = TrayState.WAITING
        self._current_role: str = ""
        self._on_open_settings: Optional[Callable[[], None]] = None
        self._on_toggle_hud: Optional[Callable[[], None]] = None
        self._on_role_changed: Optional[Callable[[str], None]] = None
        self._on_quit: Optional[Callable[[], None]] = None

        self._build_icon()
        self._build_menu()
        self.setToolTip("D2Hub — Ожидание Dota...")

    @property
    def state(self) -> TrayState:
        return self._state

    def set_state(self, state: TrayState) -> None:
        """Обновляет состояние и иконку."""
        self._state = state
        self._update_icon()
        tooltips = {
            TrayState.WAITING: "D2Hub — Ожидание Dota...",
            TrayState.DOTA_FOUND: "D2Hub — Dota запущена, ожидание GSI...",
            TrayState.GSI_ACTIVE: "D2Hub — GSI активен",
        }
        self.setToolTip(tooltips.get(state, "D2Hub"))
        self._update_status_action()

    def set_callbacks(
        self,
        on_open_settings: Callable[[], None] | None = None,
        on_toggle_hud: Callable[[], None] | None = None,
        on_role_changed: Callable[[str], None] | None = None,
        on_quit: Callable[[], None] | None = None,
    ) -> None:
        self._on_open_settings = on_open_settings
        self._on_toggle_hud = on_toggle_hud
        self._on_role_changed = on_role_changed
        self._on_quit = on_quit

    def set_role(self, role: str) -> None:
        """Обновляет текущую роль в меню."""
        self._current_role = role
        for action in self._role_actions:
            action.setChecked(action.data() == role)

    def _build_icon(self) -> None:
        self._update_icon()

    def _create_colored_icon(self, color: QtGui.QColor) -> QtGui.QIcon:
        pixmap = QtGui.QPixmap(16, 16)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(QtGui.QBrush(color))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawEllipse(2, 2, 12, 12)
        painter.end()
        return QtGui.QIcon(pixmap)

    def _update_icon(self) -> None:
        colors = {
            TrayState.WAITING: QtGui.QColor(128, 128, 128),
            TrayState.DOTA_FOUND: QtGui.QColor(255, 191, 88),
            TrayState.GSI_ACTIVE: QtGui.QColor(34, 197, 94),
        }
        color = colors.get(self._state, QtGui.QColor(128, 128, 128))
        self.setIcon(self._create_colored_icon(color))

    def _build_menu(self) -> None:
        menu = QtWidgets.QMenu()

        self._status_action = menu.addAction("Dota: Offline")
        self._status_action.setEnabled(False)

        menu.addSeparator()

        settings_action = menu.addAction("Открыть настройки")
        settings_action.triggered.connect(self._handle_open_settings)

        toggle_hud_action = menu.addAction("Показать/скрыть HUD")
        toggle_hud_action.triggered.connect(self._handle_toggle_hud)

        role_menu = menu.addMenu("Роль")
        self._role_actions: list[QtGui.QAction] = []
        role_group = QtGui.QActionGroup(role_menu)
        role_group.setExclusive(True)
        for key, label in ROLE_LABELS.items():
            action = role_menu.addAction(label)
            action.setCheckable(True)
            action.setData(key)
            action.triggered.connect(lambda checked, k=key: self._handle_role_changed(k))
            role_group.addAction(action)
            self._role_actions.append(action)

        menu.addSeparator()

        quit_action = menu.addAction("Выход")
        quit_action.triggered.connect(self._handle_quit)

        self.setContextMenu(menu)

    def _update_status_action(self) -> None:
        labels = {
            TrayState.WAITING: "Dota: Offline",
            TrayState.DOTA_FOUND: "Dota: Online (ожидание GSI)",
            TrayState.GSI_ACTIVE: "Dota: Online (GSI активен)",
        }
        self._status_action.setText(labels.get(self._state, "Dota: Offline"))

    def _handle_open_settings(self) -> None:
        if self._on_open_settings:
            self._on_open_settings()

    def _handle_toggle_hud(self) -> None:
        if self._on_toggle_hud:
            self._on_toggle_hud()

    def _handle_role_changed(self, role: str) -> None:
        self._current_role = role
        if self._on_role_changed:
            self._on_role_changed(role)

    def _handle_quit(self) -> None:
        if self._on_quit:
            self._on_quit()
