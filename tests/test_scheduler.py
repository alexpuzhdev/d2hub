from __future__ import annotations

from dota_hud.scheduler import Scheduler


def test_scheduler_smoke() -> None:
    scheduler = Scheduler([])
    state = scheduler.tick()

    assert state.elapsed == 0
    assert state.now is None
    assert state.next_ is None
    assert state.after is None
