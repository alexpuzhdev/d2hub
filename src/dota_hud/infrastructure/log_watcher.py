from __future__ import annotations

import os
import re
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, Optional


@dataclass(frozen=True)
class LogWatcherConfig:
    """Параметры наблюдения за логом игры."""

    path: Path
    start_patterns: Iterable[str]
    poll_interval: float
    debounce_seconds: float


class LogWatcher:
    """Наблюдает за игровым логом и сигнализирует о старте матча."""

    def __init__(
        self,
        path: str,
        start_patterns: list[str],
        on_start: Callable[[], None],
        poll_interval: float = 0.1,
        debounce_seconds: float = 5.0,
    ) -> None:
        """Создаёт наблюдатель за логом."""
        self._config = LogWatcherConfig(
            path=Path(path),
            start_patterns=start_patterns,
            poll_interval=poll_interval,
            debounce_seconds=debounce_seconds,
        )
        self._on_start = on_start
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._last_start_ts = 0.0
        self._last_log_ts: Dict[str, float] = {}
        self._patterns = [re.compile(pattern) for pattern in start_patterns if pattern]

    def start(self) -> None:
        """Запускает чтение лога."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Останавливает чтение лога."""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)

    def _run(self) -> None:
        self._log("start", f"[log] watcher started: {self._config.path}")
        while not self._stop_event.is_set():
            if not self._config.path.exists():
                self._log_throttled(
                    "missing",
                    f"[log] file not found, waiting: {self._config.path}",
                    min_interval=5.0,
                )
                self._stop_event.wait(self._config.poll_interval)
                continue
            try:
                self._tail_file()
            except Exception as exc:
                self._log_throttled(
                    "error",
                    f"[log] watcher error: {exc}",
                    min_interval=5.0,
                )
                self._stop_event.wait(self._config.poll_interval)

    def _tail_file(self) -> None:
        with self._config.path.open("r", encoding="utf-8", errors="ignore") as handle:
            handle.seek(0, os.SEEK_END)
            offset = handle.tell()
            self._log_throttled(
                "opened",
                f"[log] watching: {self._config.path}",
                min_interval=5.0,
            )

            while not self._stop_event.is_set():
                line = handle.readline()
                if line:
                    offset = handle.tell()
                    matched = self._match_pattern(line)
                    if matched:
                        self._request_start(matched)
                    continue

                try:
                    size = self._config.path.stat().st_size
                except FileNotFoundError:
                    self._log_throttled(
                        "missing",
                        f"[log] file disappeared, reopening: {self._config.path}",
                        min_interval=5.0,
                    )
                    return

                if size < offset:
                    self._log_throttled(
                        "truncated",
                        f"[log] file truncated, reopening: {self._config.path}",
                        min_interval=5.0,
                    )
                    return

                self._stop_event.wait(self._config.poll_interval)

    def _match_pattern(self, line: str) -> Optional[str]:
        for pattern in self._patterns:
            if pattern.search(line):
                return pattern.pattern
        return None

    def _request_start(self, pattern: str) -> None:
        now = time.monotonic()
        if now - self._last_start_ts < self._config.debounce_seconds:
            return
        self._last_start_ts = now
        self._log("match", f"[log] matched pattern: {pattern}")
        self._on_start()
        self._log("request", "[log] auto start requested")

    def _log(self, key: str, message: str) -> None:
        self._last_log_ts[key] = time.monotonic()
        print(message, flush=True)

    def _log_throttled(self, key: str, message: str, min_interval: float) -> None:
        now = time.monotonic()
        last = self._last_log_ts.get(key)
        if last is not None and now - last < min_interval:
            return
        self._log(key, message)
