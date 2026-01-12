from __future__ import annotations

from pathlib import Path
import threading

from .config import load_config, Window
from .events import format_mmss
from .hotkeys import Hotkeys, HotkeysConfig
from .log_watcher import LogWatcher
from .scheduler import Scheduler
from .ui.hud_tk import HudStyle, HudTk


def _fmt_items(items: list[str], max_lines: int = 2) -> str:
    lines = [f"• {x}" for x in items]
    if len(lines) > max_lines:
        lines = lines[:max_lines] + [f"• +{len(items)-max_lines} ещё"]
    return "\n".join(lines)


def _active_windows(elapsed: int, windows: list[Window]) -> list[Window]:
    """Вернуть все окна, активные в данный момент."""
    actives = [w for w in windows if w.from_t <= elapsed <= w.to_t]
    actives.sort(key=lambda w: w.priority, reverse=True)
    return actives


def _level_of(actives: list[Window]) -> str:
    for lvl in ("danger", "warn", "info"):
        if any(w.level == lvl for w in actives):
            return lvl
    return ""


def run_app(config_path: Path) -> None:
    cfg = load_config(config_path)

    style = HudStyle(
        title=cfg.hud.title,
        width=cfg.hud.width,
        height=cfg.hud.height,
        x=cfg.hud.x,
        y=cfg.hud.y,
        alpha=cfg.hud.alpha,
        font_family=cfg.hud.font_family,
        font_size=cfg.hud.font_size,
        font_weight=cfg.hud.font_weight,
    )

    hud = HudTk(style)
    scheduler = Scheduler(cfg.buckets)
    auto_start_event = threading.Event()
    watcher = None
    hotkeys = Hotkeys(
        HotkeysConfig(
            start=cfg.hotkeys.start,
            stop=cfg.hotkeys.stop,
            reset=cfg.hotkeys.reset,
            lock=cfg.hotkeys.lock,
        )
    )
    hotkeys.start()

    if cfg.log_integration.enabled:
        watcher = LogWatcher(
            path=cfg.log_integration.path,
            start_patterns=cfg.log_integration.start_patterns,
            on_start=auto_start_event.set,
            poll_interval=cfg.log_integration.poll_interval_ms / 1000.0,
            debounce_seconds=cfg.log_integration.debounce_seconds,
        )
        watcher.start()

    def on_close() -> None:
        if watcher:
            watcher.stop()
        hud.close()

    hud.set_on_close(on_close)

    def loop() -> None:
        hud.every(200, loop)

        try:
            if auto_start_event.is_set():
                auto_start_event.clear()
                if not scheduler.is_running:
                    scheduler.reset()
                    scheduler.start()

            for action in hotkeys.drain():
                if action == "stop":
                    scheduler.stop()
                elif action == "reset":
                    scheduler.reset()
                elif action == "start":
                    if not scheduler.is_running:
                        scheduler.start()
                elif action == "lock":
                    hud.toggle_lock()

            st = scheduler.tick()
            hud.set_timer(format_mmss(st.elapsed))

            actives = _active_windows(st.elapsed, cfg.windows)
            level = _level_of(actives)
            hud.set_warning(level)

            # Показываем активное окно (самое приоритетное)
            if actives:
                top = actives[0]
                hud.set_now(f"{format_mmss(top.from_t)}–{format_mmss(top.to_t)}  {top.text}")
            else:
                if not scheduler.is_running:
                    hud.set_now("READY  |  F8 START  F9 STOP  F10 RESET  F7 LOCK")
                elif st.now:
                    hud.set_now(f"NOW @ {format_mmss(st.now.t)}\n{_fmt_items(st.now.items)}")
                else:
                    hud.set_now("OK")

            if st.next_:
                left = st.next_.t - st.elapsed
                hud.set_next(f"NEXT {format_mmss(st.next_.t)}  ({left}s)\n{_fmt_items(st.next_.items)}")
            else:
                hud.set_next("NEXT: —")

            if st.after:
                hud.set_after(f"AFTER {format_mmss(st.after.t)}\n{_fmt_items(st.after.items)}")
            else:
                hud.set_after("AFTER: —")

        except Exception as e:
            hud.set_now(f"HUD error: {e}")

    hud.every(200, loop)
    try:
        hud.run()
    finally:
        hotkeys.stop()
        if watcher:
            watcher.stop()
