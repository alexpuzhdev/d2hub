from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from ..domain.events import Bucket
from ..domain.warning_windows import WarningWindow


@dataclass(frozen=True)
class HudConfig:
    """Настройки отображения HUD."""

    title: str = "Dota HUD"
    width: int = 560
    height: int = 190
    x: int = 30
    y: int = 30
    alpha: float = 0.92
    font_family: str = "Segoe UI"
    font_size: int = 18
    font_weight: str = "bold"


@dataclass(frozen=True)
class HotkeysConfig:
    """Настройки горячих клавиш."""

    start: str = "F8"
    stop: str = "F9"
    reset: str = "F10"
    lock: str = "F7"


@dataclass(frozen=True)
class LogIntegrationConfig:
    """Настройки интеграции с игровыми логами."""

    enabled: bool = False
    path: str = ""
    start_patterns: List[str] = field(
        default_factory=lambda: [
            "GAME_IN_PROGRESS",
            "DOTA_GAMERULES_STATE_GAME_IN_PROGRESS",
        ]
    )
    poll_interval_ms: int = 100
    debounce_seconds: float = 5.0


@dataclass(frozen=True)
class AppConfig:
    """Сводная конфигурация приложения HUD."""

    hud: HudConfig
    hotkeys: HotkeysConfig
    log_integration: LogIntegrationConfig
    buckets: List[Bucket]
    windows: List[WarningWindow]
