from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ...domain.scheduler import Scheduler
from ...domain.warning_windows import WarningWindow, WarningWindowService
from ..hud_presenter import HudPresenter
from ..models import HudState
from ..models import GameStateSnapshot


@dataclass(frozen=True)
class HudCycleResult:
    """Результат обновления HUD за один цикл."""

    hud_state: HudState
    paused_status: str | None


class HudCycleUseCase:
    """Выполняет вычисления HUD на одном тике."""

    def __init__(
        self,
        scheduler: Scheduler,
        warning_service: WarningWindowService,
        presenter: HudPresenter,
        windows: list[WarningWindow],
    ) -> None:
        """Создаёт use-case обновления HUD."""
        self._scheduler = scheduler
        self._warning_service = warning_service
        self._presenter = presenter
        self._windows = windows

    def run(
        self,
        gsi_state: GameStateSnapshot | None,
        actions: Iterable[str],
    ) -> HudCycleResult:
        """Обновляет тайминги и возвращает состояние HUD."""
        paused_status = None

        if gsi_state and gsi_state.clock_time is not None:
            self._scheduler.set_external_elapsed(gsi_state.clock_time)

            if gsi_state.paused:
                paused_status = "PAUSED (DOTA)"

        for action in actions:
            if action == "stop":
                self._scheduler.stop()
            elif action == "reset":
                self._scheduler.reset()
            elif action == "start":
                self._scheduler.start()

        tick_state = self._scheduler.tick()
        active_windows = self._warning_service.active_windows(
            tick_state.elapsed,
            self._windows,
        )
        warning_level = self._warning_service.warning_level(active_windows)
        warning_text = active_windows[0].text if active_windows else None
        hud_state = self._presenter.build_view_model(
            tick_state,
            warning_text=warning_text,
            warning_level=warning_level,
        )

        return HudCycleResult(hud_state=hud_state, paused_status=paused_status)
