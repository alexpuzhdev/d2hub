from __future__ import annotations

from pathlib import Path
from typing import Callable

from dota_hud.application.app_controller import AppController
from dota_hud.config.loader import load_config


class FakeHud:
    """Заглушка HUD для тестов."""

    def __init__(self) -> None:
        """Создаёт заглушку HUD."""
        self.closed = False
        self.on_close = None

    def set_warning(self, level: str | bool) -> None:
        """Принимает уровень предупреждения."""

    def set_timer(self, text: str) -> None:
        """Принимает текст таймера."""

    def set_now(self, text: str) -> None:
        """Принимает текст NOW."""

    def set_next(self, text: str) -> None:
        """Принимает текст NEXT."""

    def set_after(self, text: str) -> None:
        """Принимает текст AFTER."""

    def every(self, ms: int, fn: Callable[[], None]) -> None:
        """Принимает планирование таймера."""

    def set_on_close(self, callback: Callable[[], None]) -> None:
        """Сохраняет обработчик закрытия."""
        self.on_close = callback

    def toggle_lock(self) -> None:
        """Переключает блокировку."""

    def run(self) -> None:
        """Запускает цикл HUD."""

    def close(self) -> None:
        """Закрывает HUD."""
        self.closed = True


def _write_config(tmp_path: Path, text: str) -> Path:
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(text, encoding="utf-8")
    return cfg_path


def test_create_app_controller(tmp_path: Path) -> None:
    cfg_path = _write_config(tmp_path, "{}")
    config = load_config(cfg_path)

    controller = AppController(config, hud=FakeHud())

    assert controller is not None
