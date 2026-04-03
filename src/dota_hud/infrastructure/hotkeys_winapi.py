from __future__ import annotations

import ctypes
import ctypes.wintypes
import logging
import threading
from queue import Empty, SimpleQueue
from typing import List

from ..application.commands import HudAction
from ..config.models import HotkeysConfig

logger = logging.getLogger(__name__)

VK_CODES: dict[str, int] = {
    "F1": 0x70, "F2": 0x71, "F3": 0x72, "F4": 0x73,
    "F5": 0x74, "F6": 0x75, "F7": 0x76, "F8": 0x77,
    "F9": 0x78, "F10": 0x79, "F11": 0x7A, "F12": 0x7B,
}

MOD_NOREPEAT = 0x4000
WM_HOTKEY = 0x0312
HOTKEY_ID_LOCK = 1


class WinApiHotkeys:
    """Горячие клавиши через WinAPI RegisterHotKey."""

    def __init__(self, config: HotkeysConfig) -> None:
        self._config = config
        self._queue: SimpleQueue[HudAction] = SimpleQueue()
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def drain(self, max_items: int = 30) -> List[HudAction]:
        actions: List[HudAction] = []
        for _ in range(max_items):
            try:
                actions.append(self._queue.get_nowait())
            except Empty:
                break
        return actions

    def _run(self) -> None:
        user32 = ctypes.windll.user32  # type: ignore[attr-defined]
        vk = VK_CODES.get(self._config.lock.upper())
        if vk is None:
            logger.error("Unknown hotkey: %s", self._config.lock)
            return
        if not user32.RegisterHotKey(None, HOTKEY_ID_LOCK, MOD_NOREPEAT, vk):
            logger.error("Failed to register hotkey %s", self._config.lock)
            return
        logger.info("Registered hotkey %s (vk=0x%X)", self._config.lock, vk)
        msg = ctypes.wintypes.MSG()
        try:
            while not self._stop_event.is_set():
                if user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
                    if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID_LOCK:
                        self._queue.put(HudAction.LOCK)
                else:
                    self._stop_event.wait(timeout=0.05)
        finally:
            user32.UnregisterHotKey(None, HOTKEY_ID_LOCK)
