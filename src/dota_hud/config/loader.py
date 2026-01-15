from __future__ import annotations

from pathlib import Path

from .mapper import map_config
from .models import AppConfig
from .reader import read_config


def load_config(path: Path) -> AppConfig:
    """Загружает конфигурацию из YAML файла."""
    data = read_config(path)
    macro_config = data.get("macro_config")
    if macro_config and not data.get("macro_timings"):
        macro_path = (path.parent / str(macro_config)).resolve()
        macro_data = read_config(macro_path)
        if isinstance(macro_data, list):
            data["macro_timings"] = macro_data
        elif isinstance(macro_data, dict):
            data["macro_timings"] = macro_data.get("macro_timings", [])
            if "macro_hints" in macro_data and not data.get("macro_hints"):
                data["macro_hints"] = macro_data.get("macro_hints", [])
    return map_config(data)
