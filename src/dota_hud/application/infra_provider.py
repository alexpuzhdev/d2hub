from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Optional

from ..config.models import AppConfig
from ..infrastructure.gsi_server import GSIServer, GSIState
from ..infrastructure.hotkeys import Hotkeys
from ..infrastructure.log_watcher import LogWatcher
from .ports import GsiServerPort, HotkeysPort, LogWatcherPort


class GsiStateStore:
    """Хранилище последнего состояния GSI с блокировкой."""

    def __init__(self) -> None:
        """Создаёт хранилище состояния."""
        self._lock = threading.Lock()
        self._state: Optional[GSIState] = None
        self._last_update_ts: float | None = None
        self._last_heartbeat_ts: float | None = None

    def update(self, state: GSIState) -> None:
        """Обновляет сохранённое состояние GSI."""
        with self._lock:
            self._state = state
            self._last_update_ts = state.updated_at or time.time()

    def get(self) -> Optional[GSIState]:
        """Возвращает текущее состояние GSI."""
        with self._lock:
            return self._state

    def mark_heartbeat(self) -> None:
        """Фиксирует получение heartbeat от GSI."""
        with self._lock:
            self._last_heartbeat_ts = time.time()

    def last_heartbeat(self) -> Optional[float]:
        """Возвращает время последнего heartbeat."""
        with self._lock:
            return self._last_heartbeat_ts

    def last_update(self) -> Optional[float]:
        """Возвращает время последнего обновления состояния."""
        with self._lock:
            return self._last_update_ts


@dataclass(frozen=True)
class InfraServices:
    """Набор инфраструктурных сервисов приложения."""

    gsi_state_store: GsiStateStore
    gsi_server: GsiServerPort
    hotkeys: HotkeysPort
    log_watcher: LogWatcherPort | None


class InfraProvider:
    """Создаёт инфраструктурные сервисы по конфигурации."""

    def build(self, config: AppConfig) -> InfraServices:
        """Собирает инфраструктурные сервисы."""
        gsi_state_store = GsiStateStore()
        gsi_server = GSIServer(
            on_update=gsi_state_store.update,
            on_heartbeat=gsi_state_store.mark_heartbeat,
        )
        hotkeys = Hotkeys(config.hotkeys)
        log_watcher = self._build_log_watcher(config)

        return InfraServices(
            gsi_state_store=gsi_state_store,
            gsi_server=gsi_server,
            hotkeys=hotkeys,
            log_watcher=log_watcher,
        )

    @staticmethod
    def _build_log_watcher(config: AppConfig) -> LogWatcher | None:
        if not config.log_integration.enabled:
            return None
        return LogWatcher(
            path=config.log_integration.path,
            start_patterns=config.log_integration.start_patterns,
            on_start=lambda: None,
            poll_interval=config.log_integration.poll_interval_ms / 1000.0,
            debounce_seconds=config.log_integration.debounce_seconds,
        )


__all__ = ["GsiStateStore", "InfraProvider", "InfraServices"]
