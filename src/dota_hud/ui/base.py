from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable


class HudBase(ABC):
    @abstractmethod
    def set_drag_enabled(self, enabled: bool) -> None:
        raise NotImplementedError

    @abstractmethod
    def toggle_lock(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_lock(self, enabled: bool) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_warning(self, is_warn: bool | str) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_timer(self, text: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_now(self, text: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_next(self, text: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_after(self, text: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def every(self, ms: int, fn: Callable[[], None]) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_on_close(self, callback: Callable[[], None]) -> None:
        raise NotImplementedError

    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError
