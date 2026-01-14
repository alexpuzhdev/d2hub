from __future__ import annotations

from typing import Callable, Protocol


class HudPort(Protocol):
    """Интерфейс UI HUD для слоя приложения."""

    def set_warning(self, text: str | None, level: str | None = None) -> None:
        """Устанавливает уровень предупреждения."""

    def set_timer(self, text: str) -> None:
        """Обновляет текст таймера."""

    def set_now(self, text: str) -> None:
        """Обновляет блок NOW."""

    def set_next(self, text: str) -> None:
        """Обновляет блок NEXT."""

    def set_after(self, text: str) -> None:
        """Обновляет блок AFTER."""

    def every(self, ms: int, fn: Callable[[], None]) -> None:
        """Планирует вызов функции в цикле UI."""

    def set_on_close(self, callback: Callable[[], None]) -> None:
        """Устанавливает обработчик закрытия окна."""

    def toggle_lock(self) -> None:
        """Переключает режим блокировки."""

    def run(self) -> None:
        """Запускает цикл UI."""

    def close(self) -> None:
        """Закрывает окно HUD."""
