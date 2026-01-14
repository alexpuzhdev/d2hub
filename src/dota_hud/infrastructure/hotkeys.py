from __future__ import annotations

from queue import Empty, SimpleQueue
from typing import List

import keyboard

from ..config.models import HotkeysConfig
from ..application.commands import HudAction


class Hotkeys:
    """Регистрирует горячие клавиши и выдаёт события."""

    def __init__(self, config: HotkeysConfig) -> None:
        """Создаёт обработчик горячих клавиш."""
        self._config = config
        self._queue: SimpleQueue[HudAction] = SimpleQueue()
        self._hooks: List[int] = []

    def start(self) -> None:
        """Регистрирует горячие клавиши."""
        self.stop()
        self._hooks.append(
            keyboard.add_hotkey(self._config.start, lambda: self._queue.put(HudAction.START))
        )
        self._hooks.append(
            keyboard.add_hotkey(self._config.stop, lambda: self._queue.put(HudAction.STOP))
        )
        self._hooks.append(
            keyboard.add_hotkey(self._config.reset, lambda: self._queue.put(HudAction.RESET))
        )
        self._hooks.append(
            keyboard.add_hotkey(self._config.lock, lambda: self._queue.put(HudAction.LOCK))
        )

    def stop(self) -> None:
        """Снимает регистрацию горячих клавиш."""
        for hook in self._hooks:
            try:
                keyboard.remove_hotkey(hook)
            except Exception:
                pass
        self._hooks.clear()

    def drain(self, max_items: int = 30) -> List[HudAction]:
        """Возвращает накопленные события горячих клавиш."""
        drained: List[HudAction] = []
        for _ in range(max_items):
            try:
                drained.append(self._queue.get_nowait())
            except Empty:
                break
        return drained
