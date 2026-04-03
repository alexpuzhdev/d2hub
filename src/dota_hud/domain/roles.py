from __future__ import annotations

from enum import Enum
from typing import Optional


class Role(Enum):
    CARRY = "carry"
    MID = "mid"
    OFFLANE = "offlane"
    SOFT_SUPPORT = "soft_support"
    HARD_SUPPORT = "hard_support"


HERO_DEFAULT_ROLES: dict[str, Role] = {
    # Carry
    "npc_dota_hero_antimage": Role.CARRY,
    "npc_dota_hero_faceless_void": Role.CARRY,
    "npc_dota_hero_phantom_lancer": Role.CARRY,
    "npc_dota_hero_juggernaut": Role.CARRY,
    "npc_dota_hero_luna": Role.CARRY,
    "npc_dota_hero_slark": Role.CARRY,
    "npc_dota_hero_spectre": Role.CARRY,
    "npc_dota_hero_terrorblade": Role.CARRY,
    "npc_dota_hero_medusa": Role.CARRY,
    "npc_dota_hero_morphling": Role.CARRY,
    "npc_dota_hero_naga_siren": Role.CARRY,
    "npc_dota_hero_phantom_assassin": Role.CARRY,
    "npc_dota_hero_troll_warlord": Role.CARRY,
    "npc_dota_hero_ursa": Role.CARRY,
    "npc_dota_hero_wraith_king": Role.CARRY,
    "npc_dota_hero_lifestealer": Role.CARRY,
    "npc_dota_hero_sven": Role.CARRY,
    "npc_dota_hero_chaos_knight": Role.CARRY,
    "npc_dota_hero_drow_ranger": Role.CARRY,
    "npc_dota_hero_gyrocopter": Role.CARRY,
    "npc_dota_hero_weaver": Role.CARRY,
    "npc_dota_hero_riki": Role.CARRY,
    "npc_dota_hero_bloodseeker": Role.CARRY,
    "npc_dota_hero_razor": Role.CARRY,
    "npc_dota_hero_muerta": Role.CARRY,

    # Mid
    "npc_dota_hero_invoker": Role.MID,
    "npc_dota_hero_storm_spirit": Role.MID,
    "npc_dota_hero_shadow_fiend": Role.MID,
    "npc_dota_hero_queen_of_pain": Role.MID,
    "npc_dota_hero_puck": Role.MID,
    "npc_dota_hero_tinker": Role.MID,
    "npc_dota_hero_templar_assassin": Role.MID,
    "npc_dota_hero_ember_spirit": Role.MID,
    "npc_dota_hero_leshrac": Role.MID,
    "npc_dota_hero_lina": Role.MID,
    "npc_dota_hero_zeus": Role.MID,
    "npc_dota_hero_death_prophet": Role.MID,
    "npc_dota_hero_void_spirit": Role.MID,
    "npc_dota_hero_huskar": Role.MID,
    "npc_dota_hero_kunkka": Role.MID,
    "npc_dota_hero_tiny": Role.MID,
    "npc_dota_hero_sniper": Role.MID,

    # Offlane
    "npc_dota_hero_mars": Role.OFFLANE,
    "npc_dota_hero_axe": Role.OFFLANE,
    "npc_dota_hero_tidehunter": Role.OFFLANE,
    "npc_dota_hero_centaur": Role.OFFLANE,
    "npc_dota_hero_bristleback": Role.OFFLANE,
    "npc_dota_hero_slardar": Role.OFFLANE,
    "npc_dota_hero_legion_commander": Role.OFFLANE,
    "npc_dota_hero_underlord": Role.OFFLANE,
    "npc_dota_hero_sand_king": Role.OFFLANE,
    "npc_dota_hero_dark_seer": Role.OFFLANE,
    "npc_dota_hero_beastmaster": Role.OFFLANE,
    "npc_dota_hero_timbersaw": Role.OFFLANE,
    "npc_dota_hero_pangolier": Role.OFFLANE,
    "npc_dota_hero_primal_beast": Role.OFFLANE,
    "npc_dota_hero_doom_bringer": Role.OFFLANE,
    "npc_dota_hero_night_stalker": Role.OFFLANE,
    "npc_dota_hero_brewmaster": Role.OFFLANE,

    # Soft Support
    "npc_dota_hero_earth_spirit": Role.SOFT_SUPPORT,
    "npc_dota_hero_tusk": Role.SOFT_SUPPORT,
    "npc_dota_hero_bounty_hunter": Role.SOFT_SUPPORT,
    "npc_dota_hero_spirit_breaker": Role.SOFT_SUPPORT,
    "npc_dota_hero_nyx_assassin": Role.SOFT_SUPPORT,
    "npc_dota_hero_rubick": Role.SOFT_SUPPORT,
    "npc_dota_hero_dark_willow": Role.SOFT_SUPPORT,
    "npc_dota_hero_hoodwink": Role.SOFT_SUPPORT,
    "npc_dota_hero_mirana": Role.SOFT_SUPPORT,
    "npc_dota_hero_pudge": Role.SOFT_SUPPORT,
    "npc_dota_hero_clockwerk": Role.SOFT_SUPPORT,
    "npc_dota_hero_windrunner": Role.SOFT_SUPPORT,
    "npc_dota_hero_elder_titan": Role.SOFT_SUPPORT,
    "npc_dota_hero_treant": Role.SOFT_SUPPORT,
    "npc_dota_hero_marci": Role.SOFT_SUPPORT,

    # Hard Support
    "npc_dota_hero_crystal_maiden": Role.HARD_SUPPORT,
    "npc_dota_hero_dazzle": Role.HARD_SUPPORT,
    "npc_dota_hero_witch_doctor": Role.HARD_SUPPORT,
    "npc_dota_hero_shadow_shaman": Role.HARD_SUPPORT,
    "npc_dota_hero_lion": Role.HARD_SUPPORT,
    "npc_dota_hero_jakiro": Role.HARD_SUPPORT,
    "npc_dota_hero_vengefulspirit": Role.HARD_SUPPORT,
    "npc_dota_hero_lich": Role.HARD_SUPPORT,
    "npc_dota_hero_warlock": Role.HARD_SUPPORT,
    "npc_dota_hero_oracle": Role.HARD_SUPPORT,
    "npc_dota_hero_omniknight": Role.HARD_SUPPORT,
    "npc_dota_hero_abaddon": Role.HARD_SUPPORT,
    "npc_dota_hero_io": Role.HARD_SUPPORT,
    "npc_dota_hero_chen": Role.HARD_SUPPORT,
    "npc_dota_hero_enchantress": Role.HARD_SUPPORT,
    "npc_dota_hero_undying": Role.HARD_SUPPORT,
    "npc_dota_hero_disruptor": Role.HARD_SUPPORT,
    "npc_dota_hero_keeper_of_the_light": Role.HARD_SUPPORT,
    "npc_dota_hero_winter_wyvern": Role.HARD_SUPPORT,
    "npc_dota_hero_bane": Role.HARD_SUPPORT,
    "npc_dota_hero_shadow_demon": Role.HARD_SUPPORT,
    "npc_dota_hero_grimstroke": Role.HARD_SUPPORT,
    "npc_dota_hero_snapfire": Role.HARD_SUPPORT,
}


def default_role_for_hero(hero_name: str) -> Optional[Role]:
    return HERO_DEFAULT_ROLES.get(hero_name)
