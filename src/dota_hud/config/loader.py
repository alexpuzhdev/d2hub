from __future__ import annotations

from pathlib import Path
from typing import Dict

import yaml

from ..domain.events import Bucket, mmss_to_seconds
from ..domain.warning_windows import WarningWindow
from .models import AppConfig, HotkeysConfig, HudConfig, LogIntegrationConfig


def _merge_into(items_map: Dict[int, list[str]], timestamp: int, items: list[str]) -> None:
    if not items:
        return
    items_map.setdefault(timestamp, [])
    items_map[timestamp].extend(items)


def _items_from_obj(obj: dict) -> list[str]:
    if obj.get("items"):
        return [str(item) for item in (obj.get("items") or []) if str(item).strip()]
    if obj.get("text"):
        text = str(obj["text"]).strip()
        return [text] if text else []
    return []


def _expand_rules(rules_raw: list[dict], items_map: Dict[int, list[str]]) -> None:
    for rule in rules_raw:
        start = mmss_to_seconds(str(rule["start"]))
        until = mmss_to_seconds(str(rule["until"]))
        every = int(rule["every_seconds"])
        items = _items_from_obj(rule)

        timestamp = start
        while timestamp <= until:
            _merge_into(items_map, timestamp, items)
            timestamp += every


def load_config(path: Path) -> AppConfig:
    """Загружает конфигурацию из YAML файла."""
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    hud_data = dict(data.get("hud", {}) or {})
    hud_data.pop("ui", None)
    data.pop("ui", None)
    hud = HudConfig(**hud_data)
    hotkeys = HotkeysConfig(**(data.get("hotkeys", {}) or {}))
    log_data = dict(data.get("log_integration", {}) or {})
    if log_data.get("start_patterns") is None:
        log_data.pop("start_patterns", None)
    log_integration = LogIntegrationConfig(**log_data)

    buckets_map: Dict[int, list[str]] = {}
    for bucket in (data.get("timeline", []) or []):
        timestamp = mmss_to_seconds(str(bucket["at"]))
        _merge_into(buckets_map, timestamp, _items_from_obj(bucket))
    for event in (data.get("events", []) or []):
        timestamp = mmss_to_seconds(str(event["at"]))
        _merge_into(buckets_map, timestamp, _items_from_obj(event))
    _expand_rules((data.get("rules", []) or []), buckets_map)

    buckets = [Bucket(t=timestamp, items=items) for timestamp, items in buckets_map.items()]
    buckets.sort(key=lambda bucket: bucket.t)

    danger_windows: list[tuple[int, int, str]] = []
    for window in (data.get("danger_windows", []) or []):
        from_time = mmss_to_seconds(str(window["from"]))
        to_time = mmss_to_seconds(str(window["to"]))
        text = str(window.get("text", "")).strip()
        if not text:
            continue
        danger_windows.append((from_time, to_time, text))

    windows: list[WarningWindow] = []
    for window in (data.get("windows", []) or []):
        from_time = mmss_to_seconds(str(window["from"]))
        to_time = mmss_to_seconds(str(window["to"]))
        text = str(window.get("text", "")).strip()
        if not text:
            continue
        level = str(window.get("level", "info")).lower()
        priority = int(window.get("priority", 0) or 0)
        windows.append(
            WarningWindow(
                from_t=from_time,
                to_t=to_time,
                text=text,
                level=level,
                priority=priority,
            )
        )
    windows.sort(key=lambda window: window.from_t)

    return AppConfig(
        hud=hud,
        hotkeys=hotkeys,
        log_integration=log_integration,
        buckets=buckets,
        danger_windows=danger_windows,
        windows=windows,
    )
