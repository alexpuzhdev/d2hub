from __future__ import annotations

import logging
import subprocess
import threading
from typing import Callable, Optional

logger = logging.getLogger(__name__)

PROCESS_NAME = "dota2.exe"


class DotaDetector:
    def __init__(
        self,
        process_name: str = PROCESS_NAME,
        poll_interval: float = 5.0,
        on_found: Callable[[], None] | None = None,
        on_lost: Callable[[], None] | None = None,
    ) -> None:
        self._process_name = process_name
        self._poll_interval = poll_interval
        self._on_found = on_found
        self._on_lost = on_lost
        self._was_running = False
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def is_running(self) -> bool:
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"IMAGENAME eq {self._process_name}"],
                capture_output=True, text=True, timeout=5,
            )
            return self._process_name.lower() in result.stdout.lower()
        except Exception:
            logger.debug("Failed to check process %s", self._process_name, exc_info=True)
            return False

    def start(self) -> None:
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=10)

    def _poll_loop(self) -> None:
        while not self._stop_event.is_set():
            running = self.is_running()
            if running and not self._was_running:
                logger.info("Dota 2 detected")
                if self._on_found:
                    self._on_found()
            elif not running and self._was_running:
                logger.info("Dota 2 closed")
                if self._on_lost:
                    self._on_lost()
            self._was_running = running
            self._stop_event.wait(timeout=self._poll_interval)
