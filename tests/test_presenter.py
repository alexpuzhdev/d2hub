from __future__ import annotations

from dota_hud.application.hud_presenter import HudPresenter, PresenterConfig
from dota_hud.domain.events import Bucket
from dota_hud.domain.scheduler import TickState


def test_macro_hints_and_limit() -> None:
    presenter = HudPresenter(
        PresenterConfig(
            macro_hints=("Tip 1", "Tip 2", "Tip 3"),
            macro_max_lines=2,
            macro_timings=(),
        )
    )
    tick_state = TickState(elapsed=0, now=None, next_event=None, after_event=None)

    view_model = presenter.build_view_model(tick_state)

    assert view_model.macro_text.startswith("MACRO:")
    assert "Tip 1" in view_model.macro_text
    assert "+1 ещё" in view_model.macro_text
