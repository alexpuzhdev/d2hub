from __future__ import annotations

from dataclasses import dataclass

from ..domain.events import format_mmss
from ..domain.macro_info import DEFAULT_MACRO_TIMINGS, MacroTiming
from ..domain.scheduler import TickState
from .models import HudState, MacroLine, WarningState


@dataclass(frozen=True)
class PresenterConfig:
    """Настройки отображения текстовых блоков."""

    max_lines: int = 2
    macro_max_lines: int = 6
    macro_timings: tuple[MacroTiming, ...] = DEFAULT_MACRO_TIMINGS
    macro_hints: tuple[str, ...] = ()


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
                f"СЕЙЧАС {format_mmss(tick_state.now.t)}\n"
                f"{self._format_items(tick_state.now.items)}"
            )
        if event_text is None:
            event_text = "СЕЙЧАС: —"

        next_text = "ДАЛЕЕ: —"
        if tick_state.next_event:
            left = tick_state.next_event.t - tick_state.elapsed
            next_text = (
                f"ДАЛЕЕ {format_mmss(tick_state.next_event.t)} ({left}с)\n"
                f"{self._format_items(tick_state.next_event.items)}"
            )

        macro_lines = self._build_macro_lines(tick_state)
        macro_text = "MACRO: —"
        if macro_lines:
            macro_text = "\n".join(["MACRO:", *[line.text for line in macro_lines]])

        return HudState(
            timer_text=format_mmss(tick_state.elapsed),
            now_text=event_text,
            now_level=None,
            next_text=next_text,
            next_level=None,
            macro_text=macro_text,
            macro_level=None,
            macro_lines=tuple(macro_lines),
            warning=WarningState(text=warning_text, level=warning_level),
        )

    def _format_items(self, items: list[str]) -> str:
        lines = [f"• {item}" for item in items]
        if len(lines) > self._config.max_lines:
            lines = lines[: self._config.max_lines] + [
                f"• +{len(items) - self._config.max_lines} ещё"
            ]
        return "\n".join(lines)

    @staticmethod
    def _limit_lines(lines: list[str], max_lines: int) -> list[str]:
        if max_lines <= 0 or len(lines) <= max_lines:
            return lines
        return lines[:max_lines] + [f"+{len(lines) - max_lines} ещё"]

    def _build_macro_lines(self, tick_state: TickState) -> list[MacroLine]:
        timing_lines: list[MacroLine] = []
        for timing in self._config.macro_timings:
            text = f"{timing.name}: {timing.status(tick_state.elapsed)}"
            timing_lines.append(
                MacroLine(
                    text=text,
                    progress=timing.progress(tick_state.elapsed),
                    color=timing.color,
                )
            )
        hint_lines = [MacroLine(text=hint) for hint in self._config.macro_hints]
        combined = [*timing_lines, *hint_lines]
        if self._config.macro_max_lines <= 0 or len(combined) <= self._config.macro_max_lines:
            return combined
        trimmed = combined[: self._config.macro_max_lines]
        trimmed.append(
            MacroLine(text=f"+{len(combined) - self._config.macro_max_lines} ещё")
        )
        return trimmed
