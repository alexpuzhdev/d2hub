from __future__ import annotations

from pathlib import Path

from .mapper import map_config
from .models import AppConfig
from .reader import read_config


_MERGE_KEYS = {
    "timeline",
    "events",
    "rules",
    "windows",
    "danger_windows",
    "macro_timings",
    "macro_hints",
}


def _merge_module_data(base: dict, module: dict) -> dict:
    merged = dict(base)
    for key in _MERGE_KEYS:
        base_items = merged.get(key) or []
        module_items = module.get(key) or []
        if base_items or module_items:
            merged[key] = [*base_items, *module_items]
    return merged


def load_config(path: Path) -> AppConfig:
    """Загружает конфигурацию из YAML файла."""
    data = read_config(path)
    for module_path in data.get("modules", []) or []:
        module_full_path = (path.parent / str(module_path)).resolve()
        module_data = read_config(module_full_path)
        if isinstance(module_data, dict):
            data = _merge_module_data(data, module_data)
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
