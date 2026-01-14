from __future__ import annotations

from PySide6 import QtWidgets


class QtApp:
    def __init__(self) -> None:
        self._app = QtWidgets.QApplication.instance()
        if self._app is None:
            self._app = QtWidgets.QApplication([])
        self._app.setQuitOnLastWindowClosed(False)

    @property
    def app(self) -> QtWidgets.QApplication:
        return self._app

    def exec(self) -> int:
        return self._app.exec()

    def quit(self) -> None:
        self._app.quit()
