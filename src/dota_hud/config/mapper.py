from __future__ import annotations

from typing import Dict

from ..domain.events import Bucket, mmss_to_seconds
from ..domain.macro_info import DEFAULT_MACRO_TIMINGS, MacroTiming
from ..domain.warning_windows import WarningWindow
from .models import (
    AppConfig,
    HotkeysConfig,
    HudConfig,
    LogIntegrationConfig,
    PresenterConfig,
)


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


def _text_from_obj(obj: dict) -> str:
    items = _items_from_obj(obj)
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return "\n".join(items)


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
                color=str(item.get("color")).strip() or None,
            )
        )
    return timings


def _load_macro_hints(raw: list[object] | None) -> list[str]:
    if not raw:
        return []
    hints: list[str] = []
    for item in raw:
        if isinstance(item, dict):
            hints.extend(_items_from_obj(item))
        else:
            text = str(item).strip()
            if text:
                hints.append(text)
    return hints


def _load_presenter(raw: dict | None, macro_hints: list[str]) -> PresenterConfig:
    data = dict(raw or {})
    data["macro_hints"] = macro_hints
    return PresenterConfig(**data)


def _load_hotkeys(raw: dict | None) -> HotkeysConfig:
    if not raw:
        return HotkeysConfig()
    return HotkeysConfig(lock=str(raw.get("lock", HotkeysConfig().lock)))


def map_config(data: dict) -> AppConfig:
    """Преобразует словарь YAML в конфигурацию приложения."""
    hud_data = dict(data.get("hud", {}) or {})
    hud = HudConfig(**hud_data)
    hotkeys = _load_hotkeys(dict(data.get("hotkeys", {}) or {}))
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

    windows: list[WarningWindow] = []
    for window in (data.get("windows", []) or []):
        from_time = mmss_to_seconds(str(window["from"]))
        to_time = mmss_to_seconds(str(window["to"]))
        text = _text_from_obj(window)
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
    for window in (data.get("danger_windows", []) or []):
        from_time = mmss_to_seconds(str(window["from"]))
        to_time = mmss_to_seconds(str(window["to"]))
        text = _text_from_obj(window)
        if not text:
            continue
        windows.append(
            WarningWindow(
                from_t=from_time,
                to_t=to_time,
                text=text,
                level="danger",
                priority=100,
            )
        )
    windows.sort(key=lambda window: window.from_t)

    macro_hints = _load_macro_hints(data.get("macro_hints"))
    presenter = _load_presenter(data.get("presenter"), macro_hints)

    return AppConfig(
        hud=hud,
        hotkeys=hotkeys,
        log_integration=log_integration,
        buckets=buckets,
        windows=windows,
        macro_timings=_load_macro_timings(data.get("macro_timings")),
        presenter=presenter,
    )
