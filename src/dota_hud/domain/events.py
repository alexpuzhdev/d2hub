from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Bucket:
    """Группа событий с общим временем."""

    t: int
    items: list[str]


def mmss_to_seconds(value: str) -> int:
    """Преобразует формат MM:SS в секунды."""
    normalized = value.strip()
    minutes, seconds = normalized.split(":")
    return int(minutes) * 60 + int(seconds)


def format_mmss(seconds: int) -> str:
    """Форматирует секунды в строку MM:SS."""
    return f"{seconds // 60}:{seconds % 60:02d}"
