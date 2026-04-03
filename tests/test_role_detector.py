from __future__ import annotations

from dota_hud.domain.roles import Role, default_role_for_hero, HERO_DEFAULT_ROLES


def test_role_enum():
    assert Role.CARRY.value == "carry"
    assert Role.HARD_SUPPORT.value == "hard_support"
    assert len(Role) == 5


def test_known_carry():
    assert default_role_for_hero("npc_dota_hero_antimage") == Role.CARRY


def test_known_support():
    assert default_role_for_hero("npc_dota_hero_crystal_maiden") == Role.HARD_SUPPORT


def test_known_mid():
    assert default_role_for_hero("npc_dota_hero_invoker") == Role.MID


def test_unknown_hero():
    assert default_role_for_hero("npc_dota_hero_unknown_xyz") is None


def test_hero_map_not_empty():
    assert len(HERO_DEFAULT_ROLES) > 50
