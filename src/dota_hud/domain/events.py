from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Bucket:
    """Группа событий с общим временем."""

    t: int
    items: list[str]
    roles: list[str] = field(default_factory=list)


def mmss_to_seconds(value: str) -> int:
    """Преобразует формат MM:SS в секунды."""
    normalized = value.strip()
    minutes, seconds = normalized.split(":")
    return int(minutes) * 60 + int(seconds)


def format_mmss(seconds: int) -> str:
    """Форматирует секунды в строку MM:SS."""
    return f"{seconds // 60}:{seconds % 60:02d}"
