from __future__ import annotations

from dataclasses import dataclass

from ..domain.events import format_mmss
from ..domain.macro_info import DEFAULT_MACRO_TIMINGS, MacroTiming, build_macro_lines
from ..domain.scheduler import TickState
from .models import HudState, WarningState


@dataclass(frozen=True)
class PresenterConfig:
    """Настройки отображения текстовых блоков."""

    max_lines: int = 2
    macro_timings: tuple[MacroTiming, ...] = DEFAULT_MACRO_TIMINGS


class HudPresenter:
    """Формирует текстовые блоки для HUD."""

    def __init__(self, config: PresenterConfig | None = None) -> None:
        """Создаёт форматтер текста HUD."""
        self._config = config or PresenterConfig()

    def build_view_model(
        self,
        tick_state: TickState,
        warning_text: str | None = None,
        warning_level: str | None = None,
    ) -> HudState:
        """Собирает модель отображения для текущего состояния."""
        event_text = None
        if tick_state.now:
            event_text = (
                f"NOW @ {format_mmss(tick_state.now.t)}\n"
                f"{self._format_items(tick_state.now.items)}"
            )
        if event_text is None:
            event_text = "NOW: —"

        next_text = "ДАЛЕЕ: —"
        if tick_state.next_event:
            left = tick_state.next_event.t - tick_state.elapsed
            next_text = (
                f"ДАЛЕЕ {format_mmss(tick_state.next_event.t)} ({left}с)\n"
                f"{self._format_items(tick_state.next_event.items)}"
            )

        after_text = "ПОТОМ: —"
        if tick_state.after_event:
            after_text = (
                f"ПОТОМ {format_mmss(tick_state.after_event.t)}\n"
                f"{self._format_items(tick_state.after_event.items)}"
            )

        macro_lines = build_macro_lines(tick_state.elapsed, self._config.macro_timings)
        if macro_lines:
            after_text = "\n".join([after_text, "MACRO:", *macro_lines])

        return HudState(
            timer_text=format_mmss(tick_state.elapsed),
            now_text=event_text,
            next_text=next_text,
            after_text=after_text,
            warning=WarningState(text=warning_text, level=warning_level),
        )

    def _format_items(self, items: list[str]) -> str:
        lines = [f"• {item}" for item in items]
        if len(lines) > self._config.max_lines:
            lines = lines[: self._config.max_lines] + [
                f"• +{len(items) - self._config.max_lines} ещё"
            ]
        return "\n".join(lines)
