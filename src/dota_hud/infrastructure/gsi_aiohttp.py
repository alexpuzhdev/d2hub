from __future__ import annotations

import asyncio
import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Callable, Optional

from aiohttp import web

logger = logging.getLogger(__name__)


@dataclass
class GSIState:
    """Снимок состояния GSI с расширенными полями."""

    clock_time: Optional[int] = None
    game_state: Optional[str] = None
    paused: bool = False
    updated_at: float = 0.0

    # Hero
    hero_name: Optional[str] = None
    hero_level: int = 0

    # Player
    player_kills: int = 0
    player_deaths: int = 0
    player_assists: int = 0
    player_gpm: int = 0
    player_last_hits: int = 0
    player_wards_placed: int = 0

    # Items: slot_name -> item_name
    items: dict[str, str] = field(default_factory=dict)


class AioGsiServer:
    """Async HTTP сервер для приёма GSI событий."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 4000,
        on_update: Callable[[GSIState], None] | None = None,
        on_heartbeat: Callable[[], None] | None = None,
    ) -> None:
        self._host = host
        self._port = port
        self._on_update = on_update
        self._on_heartbeat = on_heartbeat
        self._lock = threading.Lock()
        self.state = GSIState()
        self._runner: web.AppRunner | None = None
        self._site: web.TCPSite | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._actual_port: int = port

    @property
    def port(self) -> int:
        return self._actual_port

    async def _handle_post(self, request: web.Request) -> web.Response:
        try:
            payload = await request.json()
        except Exception:
            return web.Response(status=400)

        map_data = payload.get("map", {})
        hero_data = payload.get("hero", {})
        player_data = payload.get("player", {})
        items_data = payload.get("items", {})

        items: dict[str, str] = {}
        for key, val in items_data.items():
            if isinstance(val, dict) and "name" in val:
                name = val["name"]
                if name and name != "empty":
                    items[key] = name

        with self._lock:
            self.state.clock_time = map_data.get("clock_time")
            self.state.game_state = map_data.get("game_state")
            self.state.paused = bool(map_data.get("paused", False))
            self.state.updated_at = time.time()
            self.state.hero_name = hero_data.get("name")
            self.state.hero_level = hero_data.get("level", 0)
            self.state.player_kills = player_data.get("kills", 0)
            self.state.player_deaths = player_data.get("deaths", 0)
            self.state.player_assists = player_data.get("assists", 0)
            self.state.player_gpm = player_data.get("gpm", 0)
            self.state.player_last_hits = player_data.get("last_hits", 0)
            self.state.player_wards_placed = player_data.get("wards_placed", 0)
            self.state.items = items

            state_copy = GSIState(
                clock_time=self.state.clock_time,
                game_state=self.state.game_state,
                paused=self.state.paused,
                updated_at=self.state.updated_at,
                hero_name=self.state.hero_name,
                hero_level=self.state.hero_level,
                player_kills=self.state.player_kills,
                player_deaths=self.state.player_deaths,
                player_assists=self.state.player_assists,
                player_gpm=self.state.player_gpm,
                player_last_hits=self.state.player_last_hits,
                player_wards_placed=self.state.player_wards_placed,
                items=dict(self.state.items),
            )

        logger.debug("GSI state: %s", state_copy)

        if self._on_update:
            self._on_update(state_copy)
        if self._on_heartbeat:
            self._on_heartbeat()

        return web.Response(status=200)

    def _create_app(self) -> web.Application:
        app = web.Application()
        app.router.add_post("/", self._handle_post)
        return app

    async def start(self) -> None:
        app = self._create_app()
        self._runner = web.AppRunner(app)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, self._host, self._port)
        await self._site.start()
        sockets = self._site._server.sockets  # type: ignore[union-attr]
        if sockets:
            self._actual_port = sockets[0].getsockname()[1]
        logger.info("GSI server started on %s:%s", self._host, self._actual_port)

    async def stop(self) -> None:
        if self._runner:
            await self._runner.cleanup()
        logger.info("GSI server stopped")

    def start_in_thread(self) -> None:
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _run_loop(self) -> None:
        assert self._loop is not None
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self.start())
        self._loop.run_forever()

    def stop_from_thread(self) -> None:
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(self.stop(), self._loop)
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=5.0)
