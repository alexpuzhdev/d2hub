from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Callable, Optional


@dataclass
class GSIState:
    clock_time: Optional[int] = None
    game_state: Optional[str] = None
    paused: bool = False


class GSIServer:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 4000,
        on_update: Callable[[GSIState], None] | None = None,
    ) -> None:
        self._host = host
        self._port = port
        self._on_update = on_update
        self._lock = threading.Lock()
        self.state = GSIState()

        class Handler(BaseHTTPRequestHandler):
            def do_POST(inner_self):
                length = int(inner_self.headers.get("Content-Length", 0))
                raw = inner_self.rfile.read(length)

                try:
                    payload = json.loads(raw)
                except json.JSONDecodeError:
                    inner_self.send_response(400)
                    inner_self.end_headers()
                    return

                map_data = payload.get("map", {})

                with self._lock:
                    self.state.clock_time = map_data.get("clock_time")
                    self.state.game_state = map_data.get("game_state")
                    self.state.paused = bool(map_data.get("paused", False))

                    state_copy = GSIState(
                        clock_time=self.state.clock_time,
                        game_state=self.state.game_state,
                        paused=self.state.paused,
                    )

                if self._on_update:
                    self._on_update(state_copy)

                print("[GSI]", state_copy)

                inner_self.send_response(200)
                inner_self.end_headers()

            def log_message(self, *args) -> None:
                return

        self._server = HTTPServer((self._host, self._port), Handler)
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            daemon=True,
        )

    def start(self) -> None:
        print(f"[GSI] server started on {self._host}:{self._port}")
        self._thread.start()

    def stop(self) -> None:
        print("[GSI] server stopped")
        self._server.shutdown()
