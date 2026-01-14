from __future__ import annotations

from enum import Enum


class HudAction(str, Enum):
    """Команды управления HUD."""

    START = "start"
    STOP = "stop"
    RESET = "reset"
    LOCK = "lock"


__all__ = ["HudAction"]
