from __future__ import annotations

from dota_hud.infrastructure.build_provider import BuildInfo, StaticBuildProvider, next_item_hint, D2ptBuildProvider, ItemHint


def test_build_info():
    b = BuildInfo(hero="cm", role="sup", items_early=["boots", "cape"], items_mid=["staff"], items_late=[])
    assert b.all_items == ["boots", "cape", "staff"]


def test_next_item_first_missing():
    build = BuildInfo(hero="cm", role="sup", items_early=["boots", "cape"], items_mid=["staff"], items_late=[])
    hint = next_item_hint(build, {"slot0": "boots"})
    assert hint is not None
    assert hint.item_name == "cape"
    assert hint.stage == "early"


def test_next_item_all_bought():
    build = BuildInfo(hero="cm", role="sup", items_early=["boots"], items_mid=[], items_late=[])
    assert next_item_hint(build, {"slot0": "boots"}) is None


def test_static_provider():
    data = {"hero_cm": {"sup": {"items_early": ["boots"], "items_mid": ["cape"], "items_late": []}}}
    p = StaticBuildProvider(data)
    b = p.get_build("hero_cm", "sup")
    assert b is not None
    assert b.items_early == ["boots"]


def test_static_provider_unknown():
    assert StaticBuildProvider({}).get_build("x", "y") is None


def test_static_provider_fallback_role():
    data = {"hero_cm": {"sup": {"items_early": ["boots"], "items_mid": [], "items_late": []}}}
    b = StaticBuildProvider(data).get_build("hero_cm", "carry")
    assert b is not None  # falls back to first available role


def test_d2pt_sync_returns_none():
    p = D2ptBuildProvider()
    assert p.get_build("hero_cm", "sup") is None  # not implemented yet
