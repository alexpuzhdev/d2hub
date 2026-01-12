from __future__ import annotations

from pathlib import Path

from .app.app_controller import AppController


def run_app(config_path: Path) -> None:
    """Запускает HUD с заданной конфигурацией."""
    controller = AppController.from_config_file(config_path)
    controller.run()
