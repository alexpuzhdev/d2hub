from __future__ import annotations

from pathlib import Path
from typing import Callable

from ..config.loader import load_config
from ..config.models import AppConfig
from ..domain.scheduler import Scheduler
from ..domain.warning_windows import WarningWindowService
from ..ui.factory import UiFactory
from .commands import HudAction
from .hud_port import HudPort
from .hud_presenter import HudPresenter, PresenterConfig
from .infra_provider import InfraProvider
from .infra_provider import InfraServices
from .models import GameStateSnapshot
from .use_cases import HudCycleUseCase


class AppController:
    """Координирует работу сервисов HUD."""

    def __init__(
        self,
        config: AppConfig,
        hud: HudPort | None = None,
        infra_provider: InfraProvider | None = None,
    ) -> None:
        """Создаёт контроллер приложения."""
        self._config = config
        self._ui_factory = UiFactory()
        self._hud = hud or self._build_hud(config)
        self._scheduler = Scheduler(config.buckets)
        self._warning_service = WarningWindowService()
        self._presenter = HudPresenter(
            PresenterConfig(
                max_lines=self._config.presenter.max_lines,
                macro_max_lines=self._config.presenter.macro_max_lines,
                macro_timings=tuple(self._config.macro_timings),
                macro_hints=tuple(self._config.presenter.macro_hints),
            )
        )
        self._cycle = HudCycleUseCase(
            scheduler=self._scheduler,
            warning_service=self._warning_service,
            presenter=self._presenter,
            windows=self._config.windows,
            resync_threshold_seconds=self._config.log_integration.resync_threshold_seconds,
            gsi_timeout_seconds=self._config.log_integration.gsi_timeout_seconds,
        )

        self._current_role: str | None = None
        self._on_admin: Callable[[], None] | None = None

        provider = infra_provider or InfraProvider()
        services = provider.build(config)
        self._apply_infra(services)

        self._hud.set_on_close(self._on_close)

    def run(self) -> None:
        """Запускает основной цикл приложения (для обратной совместимости)."""
        self._gsi_server.start()
        self._hotkeys.start()
        if self._log_watcher:
            self._log_watcher.start()

        self._hud.every(200, self._loop)

        try:
            self._hud.run()
        finally:
            self._shutdown_services()

    def start_services(self) -> None:
        """Запускает GSI сервер, хоткеи и показывает HUD."""
        self._gsi_server.start()
        self._hotkeys.start()
        if self._log_watcher:
            self._log_watcher.start()
        self._hud.show()
        self._hud.every(200, self._loop)

    def stop_services(self) -> None:
        """Останавливает сервисы и скрывает HUD."""
        self._shutdown_services()
        self._hud.hide()

    def toggle_hud_visibility(self) -> None:
        """Переключает видимость HUD."""
        if self._hud.isVisible():
            self._hud.hide()
        else:
            self._hud.show()

    def set_role(self, role: str) -> None:
        """Устанавливает текущую роль."""
        self._current_role = role

    def set_on_admin(self, callback: Callable[[], None]) -> None:
        """Устанавливает callback для открытия админки."""
        self._on_admin = callback

    def shutdown(self) -> None:
        """Полное завершение."""
        self._shutdown_services()
        self._hud.close()

    def reload_config(self, config_path: "Path") -> None:
        """Перезагружает конфиг без перезапуска."""
        from ..config.loader import load_config
        config = load_config(config_path)
        self._config = config
        self._scheduler = Scheduler(config.buckets)
        self._cycle = HudCycleUseCase(
            scheduler=self._scheduler,
            warning_service=self._warning_service,
            presenter=self._presenter,
            windows=config.windows,
            resync_threshold_seconds=config.log_integration.resync_threshold_seconds,
            gsi_timeout_seconds=config.log_integration.gsi_timeout_seconds,
        )

    @staticmethod
    def from_config_file(config_path: Path) -> "AppController":
        """Создаёт контроллер из конфигурационного файла."""
        return AppController(load_config(config_path))

    def _build_hud(self, config: AppConfig) -> HudPort:
        return self._ui_factory.build(config.hud)

    def _apply_infra(self, services: InfraServices) -> None:
        self._gsi_state_store = services.gsi_state_store
        self._gsi_server = services.gsi_server
        self._hotkeys = services.hotkeys
        self._log_watcher = services.log_watcher

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
            game_state = (
                GameStateSnapshot(
                    clock_time=gsi_state.clock_time,
                    paused=gsi_state.paused,
                    updated_at=gsi_state.updated_at,
                )
                if gsi_state
                else None
            )

            actions = self._hotkeys.drain()
            if HudAction.LOCK in actions:
                self._hud.toggle_lock()
            if HudAction.ADMIN in actions and self._on_admin:
                self._on_admin()
            cycle_actions = [
                a for a in actions if a not in (HudAction.LOCK, HudAction.ADMIN)
            ]
            cycle = self._cycle.run(
                game_state,
                cycle_actions,
                last_heartbeat=self._gsi_state_store.last_heartbeat(),
                role=self._current_role,
            )
            view_model = cycle.hud_state

            self._hud.set_timer(view_model.timer_text)
            self._hud.set_warning(view_model.warning.text, view_model.warning.level)
            self._hud.set_now(
                cycle.paused_status or view_model.now_text,
                view_model.now_level,
            )

            self._hud.set_next(view_model.next_text, view_model.next_level)
            self._hud.set_macro(
                view_model.macro_text,
                view_model.macro_level,
                list(view_model.macro_lines),
            )
        except Exception as exc:
            self._hud.set_now(f"HUD error: {exc}")
