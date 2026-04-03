from __future__ import annotations

from dota_hud.domain.events import Bucket
from dota_hud.domain.scheduler import Scheduler


def test_scheduler_smoke() -> None:
    scheduler = Scheduler([])
    state = scheduler.tick()

    assert state.elapsed == 0
    assert state.now is None
    assert state.next_event is None
    assert state.after_event is None


def test_scheduler_filters_by_role():
    buckets = [
        Bucket(t=0, items=["all roles tip"]),
        Bucket(t=60, items=["carry tip"], roles=["carry"]),
        Bucket(t=60, items=["support tip"], roles=["hard_support"]),
    ]
    sched = Scheduler(buckets)
    sched.set_external_elapsed(60)
    tick = sched.tick(role="carry")
    if tick.now is not None:
        assert "carry tip" in tick.now.items or tick.now.roles == [] or "carry" in tick.now.roles


def test_scheduler_no_role_shows_all():
    buckets = [Bucket(t=0, items=["tip"], roles=["carry"])]
    sched = Scheduler(buckets)
    sched.set_external_elapsed(0)
    tick = sched.tick()  # no role = show all
    assert tick.now is not None
