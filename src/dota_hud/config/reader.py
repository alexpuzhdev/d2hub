from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def read_config(path: Path) -> dict[str, Any]:
    """Читает YAML конфигурацию и возвращает словарь."""
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
