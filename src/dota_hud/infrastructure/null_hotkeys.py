from __future__ import annotations

from ..application.commands import HudAction
from ..application.ports import HotkeysPort


class NullHotkeys(HotkeysPort):
    """Пустая реализация hotkeys, когда поддержка отключена."""

    def start(self) -> None:
        """Ничего не делает."""

    def stop(self) -> None:
        """Ничего не делает."""

    def drain(self, max_items: int = 30) -> list[HudAction]:
        """Возвращает пустой список событий."""
        return []


__all__ = ["NullHotkeys"]
