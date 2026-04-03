from __future__ import annotations

from pathlib import Path
from dota_hud.config.loader import load_config
from dota_hud.domain.roles import Role, default_role_for_hero
from dota_hud.infrastructure.build_provider import StaticBuildProvider, next_item_hint, BuildInfo


def test_full_config_loads():
    config_path = Path(__file__).resolve().parents[1] / "configs" / "timings.yaml"
    config = load_config(config_path)
    assert len(config.buckets) > 0
    assert len(config.windows) > 0
    assert len(config.macro_timings) > 0


def test_role_detection_flow():
    hero = "npc_dota_hero_crystal_maiden"
    role = default_role_for_hero(hero)
    assert role == Role.HARD_SUPPORT


def test_build_hint_flow():
    build = BuildInfo(
        hero="cm", role="hard_support",
        items_early=["item_tranquil_boots", "item_glimmer_cape"],
        items_mid=["item_force_staff"],
        items_late=[],
    )
    current = {"slot0": "item_tranquil_boots"}
    hint = next_item_hint(build, current)
    assert hint is not None
    assert hint.item_name == "item_glimmer_cape"
    assert hint.stage == "early"


def test_config_has_general_section():
    config_path = Path(__file__).resolve().parents[1] / "configs" / "timings.yaml"
    config = load_config(config_path)
    assert config.general.gsi_port == 4000


def test_config_has_build_integration():
    config_path = Path(__file__).resolve().parents[1] / "configs" / "timings.yaml"
    config = load_config(config_path)
    assert config.build_integration.provider == "static"
