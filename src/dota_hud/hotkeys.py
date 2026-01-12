from __future__ import annotations

from dataclasses import dataclass
from queue import SimpleQueue, Empty
from typing import List

import keyboard


@dataclass(frozen=True)
class HotkeysConfig:
    start: str = "F8"
    stop: str = "F9"
    reset: str = "F10"
    lock: str = "F7"


class Hotkeys:
    def __init__(self, cfg: HotkeysConfig) -> None:
        self.cfg = cfg
        self._q: SimpleQueue[str] = SimpleQueue()
        self._hooks: List[int] = []

    def start(self) -> None:
        self.stop()
        self._hooks.append(keyboard.add_hotkey(self.cfg.start, lambda: self._q.put("start")))
        self._hooks.append(keyboard.add_hotkey(self.cfg.stop, lambda: self._q.put("stop")))
        self._hooks.append(keyboard.add_hotkey(self.cfg.reset, lambda: self._q.put("reset")))
        self._hooks.append(keyboard.add_hotkey(self.cfg.lock, lambda: self._q.put("lock")))

    def stop(self) -> None:
        for h in self._hooks:
            try:
                keyboard.remove_hotkey(h)
            except Exception:
                pass
        self._hooks.clear()

    def drain(self, max_items: int = 30) -> List[str]:
        out: List[str] = []
        for _ in range(max_items):
            try:
                out.append(self._q.get_nowait())
            except Empty:
                break
        return out
