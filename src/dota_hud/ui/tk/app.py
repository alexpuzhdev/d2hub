from __future__ import annotations

import tkinter as tk


class TkApp:
    def __init__(self) -> None:
        self.root = tk.Tk()

    def run(self) -> None:
        self.root.mainloop()

    def close(self) -> None:
        try:
            self.root.destroy()
        except Exception:
            pass
