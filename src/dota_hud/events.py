from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Bucket:
    t: int
    items: list[str]


def mmss_to_seconds(s: str) -> int:
    s = s.strip()
    m, sec = s.split(":")
    return int(m) * 60 + int(sec)


def format_mmss(seconds: int) -> str:
    return f"{seconds // 60}:{seconds % 60:02d}"
