from __future__ import annotations

from pathlib import Path
from .mapper import map_config
from .models import AppConfig
from .reader import read_config


def _seconds_from_value(raw: object) -> int:
    text = str(raw).strip()
    if ":" in text:
        return mmss_to_seconds(text)
    return int(text)


def _load_macro_timings(raw: list[dict] | None) -> list[MacroTiming]:
    if not raw:
        return list(DEFAULT_MACRO_TIMINGS)
    timings: list[MacroTiming] = []
    for item in raw:
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        timings.append(
            MacroTiming(
                name=name,
                first_spawn=_seconds_from_value(item.get("first_spawn", 0)),
                interval=_seconds_from_value(item.get("interval", 0)),
                up_window=_seconds_from_value(item.get("up_window", 0)),
            )
        )
    return timings


def load_config(path: Path) -> AppConfig:
    """Загружает конфигурацию из YAML файла."""
    data = read_config(path)
    return map_config(data)
