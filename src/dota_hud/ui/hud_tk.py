from __future__ import annotations

import sys
import threading
import tkinter as tk
from dataclasses import dataclass
from typing import Callable, Optional

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32

    if hasattr(wintypes, "LONG_PTR"):
        LONG_PTR = wintypes.LONG_PTR
    else:
        LONG_PTR = ctypes.c_longlong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_long

    GetWindowLongPtrW = user32.GetWindowLongPtrW
    SetWindowLongPtrW = user32.SetWindowLongPtrW
    GetWindowLongPtrW.argtypes = [wintypes.HWND, wintypes.INT]
    GetWindowLongPtrW.restype = LONG_PTR
    SetWindowLongPtrW.argtypes = [wintypes.HWND, wintypes.INT, LONG_PTR]
    SetWindowLongPtrW.restype = LONG_PTR

    SetWindowPos = user32.SetWindowPos
    SetWindowPos.argtypes = [
        wintypes.HWND, wintypes.HWND,
        wintypes.INT, wintypes.INT, wintypes.INT, wintypes.INT,
        wintypes.UINT
    ]
    SetWindowPos.restype = wintypes.BOOL

    RedrawWindow = user32.RedrawWindow
    RedrawWindow.argtypes = [wintypes.HWND, wintypes.LPRECT, wintypes.HRGN, wintypes.UINT]
    RedrawWindow.restype = wintypes.BOOL


@dataclass(frozen=True)
class HudStyle:
    title: str
    width: int
    height: int
    x: int
    y: int
    alpha: float
    font_family: str
    font_size: int
    font_weight: str


class HudTk:
    def __init__(self, style: HudStyle) -> None:
        self.root = tk.Tk()

        # Без рамки
        self.root.overrideredirect(True)

        # topmost + alpha
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", float(style.alpha))
        self.root.geometry(f"{style.width}x{style.height}+{style.x}+{style.y}")

        self.bg_normal = "#0b0b0b"
        self.bg_warn = "#201000"
        self.fg = "#ffffff"
        self.muted = "#bdbdbd"

        self.root.configure(bg=self.bg_normal)

        # Drag
        self._dx = 0
        self._dy = 0
        self._drag_enabled = True
        self._bind_drag()

        self._locked = False
        self._lock_inflight = False
        self._lock_guard = threading.Lock()

        self._wrap = max(200, int(style.width) - 24)

        # Layout
        self.top = tk.Frame(self.root, bg=self.bg_normal)
        self.top.pack(fill="both", expand=True, padx=10, pady=10)

        self.timer = tk.Label(
            self.top,
            text="0:00",
            fg=self.fg, bg=self.bg_normal,
            font=(style.font_family, style.font_size + 10, "bold"),
            anchor="w",
        )
        self.timer.grid(row=0, column=0, sticky="w")

        self.now = tk.Label(
            self.top,
            text="READY  |  F8 START  F9 STOP  F10 RESET  F7 LOCK",
            fg=self.muted, bg=self.bg_normal,
            font=(style.font_family, style.font_size, style.font_weight),
            justify="left",
            anchor="w",
            wraplength=self._wrap,
        )
        self.now.grid(row=1, column=0, sticky="w", pady=(6, 0))

        self.next = tk.Label(
            self.top,
            text="NEXT: —",
            fg=self.fg, bg=self.bg_normal,
            font=(style.font_family, style.font_size, style.font_weight),
            justify="left",
            anchor="w",
            wraplength=self._wrap,
        )
        self.next.grid(row=2, column=0, sticky="w", pady=(8, 0))

        self.after = tk.Label(
            self.top,
            text="AFTER: —",
            fg=self.muted, bg=self.bg_normal,
            font=(style.font_family, style.font_size - 1, "normal"),
            justify="left",
            anchor="w",
            wraplength=self._wrap,
        )
        self.after.grid(row=3, column=0, sticky="w", pady=(6, 0))

        self.top.grid_columnconfigure(0, weight=1)

    # ---------------- Drag ----------------
    def _bind_drag(self) -> None:
        self.root.unbind("<ButtonPress-1>")
        self.root.unbind("<B1-Motion>")
        if self._drag_enabled:
            self.root.bind("<ButtonPress-1>", self._start_move)
            self.root.bind("<B1-Motion>", self._on_move)

    def set_drag_enabled(self, enabled: bool) -> None:
        self._drag_enabled = bool(enabled)
        self._bind_drag()

    def _start_move(self, e: tk.Event) -> None:
        self._dx = int(e.x)
        self._dy = int(e.y)

    def _on_move(self, e: tk.Event) -> None:
        x = self.root.winfo_pointerx() - self._dx
        y = self.root.winfo_pointery() - self._dy
        self.root.geometry(f"+{x}+{y}")

    # ---------------- Lock / Click-through ----------------
    def toggle_lock(self) -> None:
        self.set_lock(not self._locked)

    def set_lock(self, enabled: bool) -> None:
        enabled = bool(enabled)

        with self._lock_guard:
            if self._lock_inflight:
                return
            self._lock_inflight = True

        # UI-часть мгновенно (без WinAPI)
        self._locked = enabled
        self.set_drag_enabled(not enabled)

        # если не Windows — просто "pin"
        if sys.platform != "win32":
            with self._lock_guard:
                self._lock_inflight = False
            return

        # hwnd получаем ТОЛЬКО в Tk потоке
        self.root.update_idletasks()
        hwnd_root = int(self.root.winfo_id())

        def worker() -> None:
            err: Optional[str] = None
            try:
                self._apply_clickthrough_root(hwnd_root, enabled)
            except Exception as e:
                err = str(e)

            def done() -> None:
                # даже если ошибка — HUD должен продолжать жить
                if err:
                    # просто покажем в NOW (чтобы ты видел проблему)
                    self.set_now(f"LOCK error: {err}\nF7 to retry")
                with self._lock_guard:
                    self._lock_inflight = False

            self.root.after(0, done)

        threading.Thread(target=worker, daemon=True).start()

    def _apply_clickthrough_root(self, hwnd: int, enabled: bool) -> None:
        # ВАЖНО:
        # - WS_EX_LAYERED оставляем (его уже ставит Tk через -alpha)
        # - НЕ трогаем child HWND вообще (иначе они могут перестать рисоваться)
        GWL_EXSTYLE = -20
        WS_EX_TRANSPARENT = 0x00000020
        WS_EX_NOACTIVATE = 0x08000000

        SWP_NOSIZE = 0x0001
        SWP_NOMOVE = 0x0002
        SWP_NOZORDER = 0x0004
        SWP_FRAMECHANGED = 0x0020

        RDW_INVALIDATE = 0x0001
        RDW_UPDATENOW = 0x0100
        RDW_ALLCHILDREN = 0x0080

        exstyle = GetWindowLongPtrW(hwnd, GWL_EXSTYLE)

        if enabled:
            exstyle |= WS_EX_TRANSPARENT
            exstyle |= WS_EX_NOACTIVATE
        else:
            exstyle &= (~WS_EX_TRANSPARENT)
            exstyle &= (~WS_EX_NOACTIVATE)

        SetWindowLongPtrW(hwnd, GWL_EXSTYLE, exstyle)
        SetWindowPos(hwnd, 0, 0, 0, 0, 0, SWP_NOSIZE | SWP_NOMOVE | SWP_NOZORDER | SWP_FRAMECHANGED)

        # форсим перерисовку
        RedrawWindow(hwnd, None, None, RDW_INVALIDATE | RDW_UPDATENOW | RDW_ALLCHILDREN)

    # ---------------- UI setters ----------------
    def set_warning(self, is_warn: bool) -> None:
        bg = self.bg_warn if is_warn else self.bg_normal
        self.root.configure(bg=bg)
        for w in (self.top, self.timer, self.now, self.next, self.after):
            w.configure(bg=bg)

    def set_timer(self, text: str) -> None:
        self.timer.config(text=text)

    def set_now(self, text: str) -> None:
        self.now.config(text=text)

    def set_next(self, text: str) -> None:
        self.next.config(text=text)

    def set_after(self, text: str) -> None:
        self.after.config(text=text)

    def every(self, ms: int, fn: Callable[[], None]) -> None:
        self.root.after(ms, fn)

    def run(self) -> None:
        self.root.mainloop()

    def close(self) -> None:
        try:
            self.root.destroy()
        except Exception:
            pass
