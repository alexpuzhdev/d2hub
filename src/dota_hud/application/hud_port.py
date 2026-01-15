from __future__ import annotations

from typing import Callable, Protocol


class HudViewPort(Protocol):
    """Интерфейс UI HUD для слоя приложения."""

    def set_warning(self, text: str | None, level: str | None = None) -> None:
        """Устанавливает уровень предупреждения."""

    def set_timer(self, text: str) -> None:
        """Обновляет текст таймера."""

    def set_now(self, text: str) -> None:
        """Обновляет блок NOW."""

    def set_next(self, text: str) -> None:
        """Обновляет блок NEXT."""

    def set_macro(self, text: str) -> None:
        """Обновляет блок MACRO."""


class HudSchedulePort(Protocol):
    """Порт планирования циклов UI."""

    def every(self, ms: int, fn: Callable[[], None]) -> None:
        """Планирует вызов функции в цикле UI."""


class HudControlPort(Protocol):
    """Порт управления окном HUD."""

    def set_on_close(self, callback: Callable[[], None]) -> None:
        """Устанавливает обработчик закрытия окна."""

    def toggle_lock(self) -> None:
        """Переключает режим блокировки."""

    def run(self) -> None:
        """Запускает цикл UI."""

    def close(self) -> None:
        """Закрывает окно HUD."""


class HudPort(HudViewPort, HudSchedulePort, HudControlPort, Protocol):
    """Совмещённый интерфейс HUD для совместимости."""


__all__ = ["HudControlPort", "HudPort", "HudSchedulePort", "HudViewPort"]
