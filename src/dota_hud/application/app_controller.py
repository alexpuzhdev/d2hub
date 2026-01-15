from __future__ import annotations

from pathlib import Path

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
            PresenterConfig(macro_timings=tuple(self._config.macro_timings))
        )
        self._cycle = HudCycleUseCase(
            scheduler=self._scheduler,
            warning_service=self._warning_service,
            presenter=self._presenter,
            windows=self._config.windows,
        )

        provider = infra_provider or InfraProvider()
        services = provider.build(config)
        self._apply_infra(services)

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
                )
                if gsi_state
                else None
            )

            actions = self._hotkeys.drain()
            if HudAction.LOCK in actions:
                self._hud.toggle_lock()
            cycle_actions = [action for action in actions if action is not HudAction.LOCK]
            cycle = self._cycle.run(game_state, cycle_actions)
            view_model = cycle.hud_state

            self._hud.set_timer(view_model.timer_text)
            self._hud.set_warning(view_model.warning.text, view_model.warning.level)
            self._hud.set_now(cycle.paused_status or view_model.now_text)

            self._hud.set_next(view_model.next_text)
            self._hud.set_macro(view_model.macro_text)
        except Exception as exc:
            self._hud.set_now(f"HUD error: {exc}")
