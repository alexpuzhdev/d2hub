from __future__ import annotations

from pathlib import Path

from dota_hud.config.loader import load_config
from dota_hud.ui.hud_style import HudStyle


def _write_config(tmp_path: Path, text: str) -> Path:
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(text, encoding="utf-8")
    return cfg_path


def test_load_config_defaults(tmp_path: Path) -> None:
    cfg_path = _write_config(
        tmp_path,
        """
        hud:
          title: "Test HUD"
        """,
    )

    cfg = load_config(cfg_path)

    assert cfg.hud.title == "Test HUD"
    assert cfg.hud.width > 0


def test_build_style_from_config(tmp_path: Path) -> None:
    cfg_path = _write_config(tmp_path, "{}")
    cfg = load_config(cfg_path)

    style = HudStyle(
        title=cfg.hud.title,
        width=cfg.hud.width,
        height=cfg.hud.height,
        x=cfg.hud.x,
        y=cfg.hud.y,
        alpha=cfg.hud.alpha,
        font_family=cfg.hud.font_family,
        font_size=cfg.hud.font_size,
        font_weight=cfg.hud.font_weight,
    )

    assert style.title == cfg.hud.title
    assert style.width == cfg.hud.width
