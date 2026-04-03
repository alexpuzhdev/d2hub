from __future__ import annotations

from dota_hud.infrastructure.hotkeys_winapi import WinApiHotkeys, VK_CODES
from dota_hud.config.models import HotkeysConfig


def test_vk_codes_contains_f_keys():
    assert "F7" in VK_CODES
    assert VK_CODES["F7"] == 0x76
    assert "DELETE" in VK_CODES
    assert len(VK_CODES) >= 12


def test_hotkeys_instantiate():
    config = HotkeysConfig(lock="F7")
    hk = WinApiHotkeys(config)
    assert hk.drain() == []


def test_hotkeys_drain_empty():
    config = HotkeysConfig(lock="F8")
    hk = WinApiHotkeys(config)
    assert hk.drain(max_items=10) == []
