from __future__ import annotations

import threading
from pathlib import Path
from typing import Optional

from ..config.loader import load_config
from ..config.models import AppConfig
from ..domain.warning_windows import WarningWindowService
from ..infrastructure.gsi_server import GSIServer, GSIState
from ..infrastructure.hotkeys import Hotkeys
from ..infrastructure.log_watcher import LogWatcher
from ..domain.scheduler import Scheduler
from ..ui.hud_tk import HudStyle, HudTk
from .hud_presenter import HudPresenter


class GsiStateStore:
    """Хранилище последнего состояния GSI с блокировкой."""

    def __init__(self) -> None:
        """Создаёт хранилище состояния."""
        self._lock = threading.Lock()
        self._state: Optional[GSIState] = None

    def update(self, state: GSIState) -> None:
        """Обновляет сохранённое состояние GSI."""
        with self._lock:
            self._state = state

    def get(self) -> Optional[GSIState]:
        """Возвращает текущее состояние GSI."""
        with self._lock:
            return self._state


class AppController:
    """Координирует работу сервисов HUD."""

    def __init__(self, config: AppConfig) -> None:
        """Создаёт контроллер приложения."""
        self._config = config
        self._hud = HudTk(self._build_style(config))
        self._scheduler = Scheduler(config.buckets)
        self._warning_service = WarningWindowService()
        self._presenter = HudPresenter()

        self._gsi_state_store = GsiStateStore()
        self._gsi_server = GSIServer(on_update=self._gsi_state_store.update)

        self._hotkeys = Hotkeys(config.hotkeys)
        self._log_watcher = self._build_log_watcher(config)

        self._hud.set_on_close(self._on_close)

    def run(self) -> None:
        """Запускает основной цикл приложения."""
        self._gsi_server.start()
        self._hotkeys.start()
        if self._log_watcher:
            self._log_watcher.start()

        self._hud.every(200, self._loop)

        try:
            self._hud.run()
        finally:
            self._shutdown_services()

    @staticmethod
    def from_config_file(config_path: Path) -> "AppController":
        """Создаёт контроллер из конфигурационного файла."""
        return AppController(load_config(config_path))

    def _build_style(self, config: AppConfig) -> HudStyle:
        return HudStyle(
            title=config.hud.title,
            width=config.hud.width,
            height=config.hud.height,
            x=config.hud.x,
            y=config.hud.y,
            alpha=config.hud.alpha,
            font_family=config.hud.font_family,
            font_size=config.hud.font_size,
            font_weight=config.hud.font_weight,
        )

    def _build_log_watcher(self, config: AppConfig) -> LogWatcher | None:
        if not config.log_integration.enabled:
            return None
        return LogWatcher(
            path=config.log_integration.path,
            start_patterns=config.log_integration.start_patterns,
            on_start=lambda: None,
            poll_interval=config.log_integration.poll_interval_ms / 1000.0,
            debounce_seconds=config.log_integration.debounce_seconds,
        )

    def _on_close(self) -> None:
        if self._log_watcher:
            self._log_watcher.stop()
        self._gsi_server.stop()
        self._hud.close()

    def _shutdown_services(self) -> None:
        self._hotkeys.stop()
        if self._log_watcher:
            self._log_watcher.stop()
        self._gsi_server.stop()

    def _loop(self) -> None:
        self._hud.every(200, self._loop)

        try:
            gsi_state = self._gsi_state_store.get()

            if gsi_state and gsi_state.clock_time is not None:
                self._scheduler.set_external_elapsed(gsi_state.clock_time)

                if gsi_state.paused:
                    self._hud.set_now("PAUSED (DOTA)")
                else:
                    self._hud.set_now("SYNCED WITH DOTA")

            for action in self._hotkeys.drain():
                if action == "stop":
                    self._scheduler.stop()
                elif action == "reset":
                    self._scheduler.reset()
                elif action == "start":
                    self._scheduler.start()
                elif action == "lock":
                    self._hud.toggle_lock()

            tick_state = self._scheduler.tick()
            active_windows = self._warning_service.active_windows(
                tick_state.elapsed,
                self._config.windows,
            )
            warning_level = self._warning_service.warning_level(active_windows)
            view_model = self._presenter.build_view_model(tick_state)

            self._hud.set_timer(view_model.timer_text)
            self._hud.set_warning(bool(warning_level))

            if view_model.now_text:
                self._hud.set_now(view_model.now_text)

            self._hud.set_next(view_model.next_text)
            self._hud.set_after(view_model.after_text)
        except Exception as exc:
            self._hud.set_now(f"HUD error: {exc}")
