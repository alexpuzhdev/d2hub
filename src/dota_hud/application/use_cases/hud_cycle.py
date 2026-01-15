from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Iterable

__all__ = ["HudCycleResult", "HudCycleUseCase"]

from ...domain.scheduler import Scheduler
from ...domain.warning_windows import WarningWindow, WarningWindowService
from ..commands import HudAction
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
        resync_threshold_seconds: int = 6,
        gsi_timeout_seconds: int = 6,
    ) -> None:
        """Создаёт use-case обновления HUD."""
        self._scheduler = scheduler
        self._warning_service = warning_service
        self._presenter = presenter
        self._windows = windows
        self._resync_threshold_seconds = resync_threshold_seconds
        self._gsi_timeout_seconds = gsi_timeout_seconds

    def run(
        self,
        gsi_state: GameStateSnapshot | None,
        actions: Iterable[HudAction],
        last_heartbeat: float | None = None,
    ) -> HudCycleResult:
        """Обновляет тайминги и возвращает состояние HUD."""
        paused_status = None

        if gsi_state and gsi_state.clock_time is not None:
            self._scheduler.set_external_elapsed(gsi_state.clock_time)

            if gsi_state.paused:
                paused_status = "PAUSED (DOTA)"
            if gsi_state.updated_at is not None:
                drift = time.time() - gsi_state.updated_at
                if drift > self._resync_threshold_seconds:
                    paused_status = "GSI STALE"
        if last_heartbeat is not None:
            since_heartbeat = time.time() - last_heartbeat
            if since_heartbeat > self._gsi_timeout_seconds:
                paused_status = "GSI OFFLINE"
        if paused_status in {"GSI STALE", "GSI OFFLINE"}:
            self._scheduler.clear_external()

        for action in actions:
            if action is HudAction.STOP:
                self._scheduler.stop()
            elif action is HudAction.RESET:
                self._scheduler.reset()
            elif action is HudAction.START:
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
