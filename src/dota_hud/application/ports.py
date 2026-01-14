from __future__ import annotations

from typing import Protocol

from ..application.commands import HudAction


class HotkeysPort(Protocol):
    """Порт источника событий горячих клавиш."""

    def start(self) -> None:
        """Запускает обработку hotkeys."""

    def stop(self) -> None:
        """Останавливает обработку hotkeys."""

    def drain(self, max_items: int = 30) -> list[HudAction]:
        """Возвращает накопленные команды."""


class LogWatcherPort(Protocol):
    """Порт наблюдателя за логом."""

    def start(self) -> None:
        """Запускает наблюдение."""

    def stop(self) -> None:
        """Останавливает наблюдение."""


class GsiServerPort(Protocol):
    """Порт сервера GSI."""

    def start(self) -> None:
        """Запускает сервер."""

    def stop(self) -> None:
        """Останавливает сервер."""


__all__ = ["GsiServerPort", "HotkeysPort", "LogWatcherPort"]
