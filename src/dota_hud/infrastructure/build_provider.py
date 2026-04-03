from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional, Protocol

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BuildInfo:
    hero: str
    role: str
    items_early: list[str] = field(default_factory=list)
    items_mid: list[str] = field(default_factory=list)
    items_late: list[str] = field(default_factory=list)

    @property
    def all_items(self) -> list[str]:
        return self.items_early + self.items_mid + self.items_late


@dataclass(frozen=True)
class ItemHint:
    item_name: str
    stage: str  # early / mid / late


def next_item_hint(build: BuildInfo, current_items: dict[str, str]) -> Optional[ItemHint]:
    owned = set(current_items.values())
    for stage, items in [("early", build.items_early), ("mid", build.items_mid), ("late", build.items_late)]:
        for item in items:
            if item not in owned:
                return ItemHint(item_name=item, stage=stage)
    return None


class BuildProviderPort(Protocol):
    def get_build(self, hero_name: str, role: str) -> Optional[BuildInfo]: ...


class StaticBuildProvider:
    def __init__(self, data: dict) -> None:
        self._data = data

    def get_build(self, hero_name: str, role: str) -> Optional[BuildInfo]:
        hero_data = self._data.get(hero_name)
        if not hero_data:
            return None
        role_data = hero_data.get(role)
        if not role_data:
            if hero_data:
                role_data = next(iter(hero_data.values()), None)
            if not role_data:
                return None
        return BuildInfo(
            hero=hero_name, role=role,
            items_early=role_data.get("items_early", []),
            items_mid=role_data.get("items_mid", []),
            items_late=role_data.get("items_late", []),
        )


class D2ptBuildProvider:
    def __init__(self, base_url: str = "https://d2pt.ru") -> None:
        self._base_url = base_url
        self._cache: dict[str, BuildInfo] = {}

    def get_build(self, hero_name: str, role: str) -> Optional[BuildInfo]:
        cache_key = f"{hero_name}:{role}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        logger.debug("d2pt API not yet implemented for %s/%s", hero_name, role)
        return None

    async def fetch_build(self, hero_name: str, role: str) -> Optional[BuildInfo]:
        import aiohttp
        cache_key = f"{hero_name}:{role}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        short_name = hero_name.replace("npc_dota_hero_", "")
        url = f"{self._base_url}/api/hero/{short_name}/build"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status != 200:
                        return None
                    data = await resp.json()
                    build = BuildInfo(
                        hero=hero_name, role=role,
                        items_early=data.get("items_early", []),
                        items_mid=data.get("items_mid", []),
                        items_late=data.get("items_late", []),
                    )
                    self._cache[cache_key] = build
                    return build
        except Exception:
            logger.debug("d2pt API error for %s", short_name, exc_info=True)
            return None
