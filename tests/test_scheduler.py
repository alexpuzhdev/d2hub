from __future__ import annotations

from dota_hud.domain.scheduler import Scheduler


def test_scheduler_smoke() -> None:
    scheduler = Scheduler([])
    state = scheduler.tick()

    assert state.elapsed == 0
    assert state.now is None
    assert state.next_event is None
    assert state.after_event is None
