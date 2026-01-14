from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Tuple
import yaml

from .events import Bucket, mmss_to_seconds


@dataclass(frozen=True)
class HudConfig:
    title: str = "Dota HUD"
    width: int = 560
    height: int = 190
    x: int = 30
    y: int = 30
    alpha: float = 0.92
    font_family: str = "Segoe UI"
    font_size: int = 15
    font_weight: str = "bold"
    ui: str = "tk"


@dataclass(frozen=True)
class UiConfig:
    choice: str = "tk"


@dataclass(frozen=True)
class HotkeysConfig:
    start: str = "F8"
    stop: str = "F9"
    reset: str = "F10"
    lock: str = "F7"


@dataclass(frozen=True)
class LogIntegrationConfig:
    enabled: bool = False
    path: str = ""
    start_patterns: List[str] = field(default_factory=lambda: [
        "GAME_IN_PROGRESS",
        "DOTA_GAMERULES_STATE_GAME_IN_PROGRESS",
    ])
    poll_interval_ms: int = 100
    debounce_seconds: float = 5.0


@dataclass(frozen=True)
class Window:
    from_t: int
    to_t: int
    text: str
    level: str = "info"
    priority: int = 0


@dataclass(frozen=True)
class AppConfig:
    hud: HudConfig
    ui: UiConfig
    hotkeys: HotkeysConfig
    log_integration: LogIntegrationConfig
    buckets: List[Bucket]
    danger_windows: List[Tuple[int, int, str]]   # для обратной совместимости
    windows: List[Window]


def _merge_into(map_: Dict[int, list[str]], t: int, items: list[str]) -> None:
    if not items:
        return
    map_.setdefault(t, [])
    map_[t].extend(items)


def _items_from_obj(obj: dict) -> list[str]:
    if obj.get("items"):
        return [str(x) for x in (obj.get("items") or []) if str(x).strip()]
    if obj.get("text"):
        s = str(obj["text"]).strip()
        return [s] if s else []
    return []


def _expand_rules(rules_raw: list[dict], map_: Dict[int, list[str]]) -> None:
    for r in rules_raw:
        start = mmss_to_seconds(str(r["start"]))
        until = mmss_to_seconds(str(r["until"]))
        every = int(r["every_seconds"])
        items = _items_from_obj(r)

        t = start
        while t <= until:
            _merge_into(map_, t, items)
            t += every


def load_config(path: Path) -> AppConfig:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    hud_data = dict(data.get("hud", {}) or {})
    ui_choice = data.get("ui") or hud_data.pop("ui", None) or "tk"
    hud = HudConfig(**hud_data)
    ui = UiConfig(choice=str(ui_choice))
    hotkeys = HotkeysConfig(**(data.get("hotkeys", {}) or {}))
    log_data = dict(data.get("log_integration", {}) or {})
    if log_data.get("start_patterns") is None:
        log_data.pop("start_patterns", None)
    log_integration = LogIntegrationConfig(**log_data)

    # ---- buckets (тайминги) ----
    buckets_map: Dict[int, list[str]] = {}
    for b in (data.get("timeline", []) or []):
        t = mmss_to_seconds(str(b["at"]))
        _merge_into(buckets_map, t, _items_from_obj(b))
    for e in (data.get("events", []) or []):
        t = mmss_to_seconds(str(e["at"]))
        _merge_into(buckets_map, t, _items_from_obj(e))
    _expand_rules((data.get("rules", []) or []), buckets_map)

    buckets = [Bucket(t=t, items=items) for t, items in buckets_map.items()]
    buckets.sort(key=lambda b: b.t)

    # ---- danger_windows (старый формат) ----
    danger_windows: list[tuple[int, int, str]] = []
    for w in (data.get("danger_windows", []) or []):
        f = mmss_to_seconds(str(w["from"]))
        to = mmss_to_seconds(str(w["to"]))
        text = str(w.get("text", "")).strip()
        if not text:
            continue
        danger_windows.append((f, to, text))

    # ---- windows (новый формат) ----
    windows: list[Window] = []
    for w in (data.get("windows", []) or []):
        f = mmss_to_seconds(str(w["from"]))
        to = mmss_to_seconds(str(w["to"]))
        text = str(w.get("text", "")).strip()
        if not text:
            continue
        level = str(w.get("level", "info")).lower()
        priority = int(w.get("priority", 0) or 0)
        windows.append(Window(from_t=f, to_t=to, text=text, level=level, priority=priority))
    windows.sort(key=lambda w: w.from_t)

    return AppConfig(
        hud=hud,
        ui=ui,
        hotkeys=hotkeys,
        log_integration=log_integration,
        buckets=buckets,
        danger_windows=danger_windows,
        windows=windows,
    )
