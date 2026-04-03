from __future__ import annotations

import pytest
import aiohttp

from dota_hud.infrastructure.gsi_aiohttp import AioGsiServer, GSIState


def test_gsi_state_defaults():
    state = GSIState()
    assert state.clock_time is None
    assert state.hero_name is None
    assert state.paused is False
    assert state.items == {}


def test_server_instantiation():
    server = AioGsiServer(host="127.0.0.1", port=0)
    assert server.state.clock_time is None


@pytest.mark.asyncio
async def test_server_handles_post():
    updates: list[GSIState] = []
    heartbeats: list[bool] = []
    server = AioGsiServer(
        host="127.0.0.1",
        port=0,
        on_update=lambda s: updates.append(s),
        on_heartbeat=lambda: heartbeats.append(True),
    )
    await server.start()
    port = server.port

    payload = {
        "map": {
            "clock_time": 300,
            "game_state": "DOTA_GAMERULES_STATE_GAME_IN_PROGRESS",
            "paused": False,
        },
        "hero": {"name": "npc_dota_hero_crystal_maiden", "level": 8},
        "player": {
            "kills": 1,
            "deaths": 2,
            "assists": 10,
            "gpm": 250,
            "last_hits": 30,
            "wards_placed": 12,
        },
        "items": {
            "slot0": {"name": "item_tranquil_boots"},
            "slot1": {"name": "item_glimmer_cape"},
            "slot2": {"name": "empty"},
        },
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"http://127.0.0.1:{port}", json=payload) as resp:
            assert resp.status == 200

    await server.stop()

    assert len(updates) == 1
    state = updates[0]
    assert state.clock_time == 300
    assert state.hero_name == "npc_dota_hero_crystal_maiden"
    assert state.hero_level == 8
    assert state.player_kills == 1
    assert state.player_deaths == 2
    assert state.player_assists == 10
    assert state.player_gpm == 250
    assert state.player_last_hits == 30
    assert state.player_wards_placed == 12
    assert "slot0" in state.items
    assert state.items["slot0"] == "item_tranquil_boots"
    assert "slot2" not in state.items  # "empty" items filtered out
    assert len(heartbeats) == 1


@pytest.mark.asyncio
async def test_server_handles_bad_json():
    server = AioGsiServer(host="127.0.0.1", port=0)
    await server.start()
    port = server.port

    async with aiohttp.ClientSession() as session:
        async with session.post(f"http://127.0.0.1:{port}", data=b"not json") as resp:
            assert resp.status == 400

    await server.stop()
