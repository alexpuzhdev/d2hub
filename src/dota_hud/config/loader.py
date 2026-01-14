from __future__ import annotations

from pathlib import Path
from .mapper import map_config
from .models import AppConfig
from .reader import read_config


def load_config(path: Path) -> AppConfig:
    """Загружает конфигурацию из YAML файла."""
    data = read_config(path)
    return map_config(data)
