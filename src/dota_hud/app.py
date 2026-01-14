from __future__ import annotations

from pathlib import Path
import threading

from .config import load_config, Window
from .events import format_mmss
from .hotkeys import Hotkeys, HotkeysConfig
from .log_watcher import LogWatcher
from .scheduler import Scheduler
from .ui import create_hud
from .ui.hud_style import HudStyle
from .gsi_server import GSIServer, GSIState


def _fmt_items(items: list[str], max_lines: int = 2) -> str:
    lines = [f"• {x}" for x in items]
    if len(lines) > max_lines:
        lines = lines[:max_lines] + [f"• +{len(items)-max_lines} ещё"]
    return "\n".join(lines)


def _active_windows(elapsed: int, windows: list[Window]) -> list[Window]:
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

    hud = create_hud(style, cfg.ui.backend, allow_tk_fallback=cfg.ui.allow_tk_fallback)
    scheduler = Scheduler(cfg.buckets)

    watcher = None
    gsi_state: GSIState | None = None
    gsi_lock = threading.Lock()

    def on_gsi_update(state: GSIState) -> None:
        nonlocal gsi_state
        with gsi_lock:
            gsi_state = state

    gsi_server = GSIServer(on_update=on_gsi_update)
    gsi_server.start()

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
            on_start=lambda: None,
            poll_interval=cfg.log_integration.poll_interval_ms / 1000.0,
            debounce_seconds=cfg.log_integration.debounce_seconds,
        )
        watcher.start()

    def on_close() -> None:
        if watcher:
            watcher.stop()
        gsi_server.stop()
        hud.close()

    hud.set_on_close(on_close)

    def loop() -> None:
        hud.every(200, loop)

        try:
            with gsi_lock:
                state = gsi_state

            # ---------- GSI УПРАВЛЕНИЕ ----------
            if state and state.clock_time is not None:
                scheduler.set_external_elapsed(state.clock_time)

                if state.paused:
                    hud.set_now("PAUSED (DOTA)")
                else:
                    hud.set_now("SYNCED WITH DOTA")

            # ---------- РУЧНЫЕ КЛАВИШИ ----------
            for action in hotkeys.drain():
                if action == "stop":
                    scheduler.stop()
                elif action == "reset":
                    scheduler.reset()
                elif action == "start":
                    scheduler.start()
                elif action == "lock":
                    hud.toggle_lock()

            st = scheduler.tick()
            hud.set_timer(format_mmss(st.elapsed))

            actives = _active_windows(st.elapsed, cfg.windows)
            hud.set_warning(_level_of(actives))

            if st.now:
                hud.set_now(
                    f"NOW @ {format_mmss(st.now.t)}\n{_fmt_items(st.now.items)}"
                )

            if st.next_:
                left = st.next_.t - st.elapsed
                hud.set_next(
                    f"NEXT {format_mmss(st.next_.t)} ({left}s)\n"
                    f"{_fmt_items(st.next_.items)}"
                )
            else:
                hud.set_next("NEXT: —")

            if st.after:
                hud.set_after(
                    f"AFTER {format_mmss(st.after.t)}\n{_fmt_items(st.after.items)}"
                )
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
        gsi_server.stop()
