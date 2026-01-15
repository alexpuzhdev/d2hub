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


def test_load_config_with_modules(tmp_path: Path) -> None:
    timeline = tmp_path / "timeline.yaml"
    timeline.write_text(
        """
        timeline:
          - at: "1:00"
            items:
              - "Первый тайминг"
        """,
        encoding="utf-8",
    )
    windows = tmp_path / "windows.yaml"
    windows.write_text(
        """
        windows:
          - from: "0:10"
            to: "0:20"
            level: warn
            text: "Тестовое окно"
        """,
        encoding="utf-8",
    )
    cfg_path = _write_config(
        tmp_path,
        """
        modules:
          - "timeline.yaml"
          - "windows.yaml"
        """,
    )

    cfg = load_config(cfg_path)

    assert len(cfg.buckets) == 1
    assert cfg.buckets[0].items == ["Первый тайминг"]
    assert len(cfg.windows) == 1
    assert cfg.windows[0].text == "Тестовое окно"


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
        margin_horizontal=cfg.hud.margin_horizontal,
        margin_vertical=cfg.hud.margin_vertical,
        spacing=cfg.hud.spacing,
        block_padding=cfg.hud.block_padding,
        text_fade_duration_ms=cfg.hud.text_fade_duration_ms,
        text_fade_start_opacity=cfg.hud.text_fade_start_opacity,
    )

    assert style.title == cfg.hud.title
    assert style.width == cfg.hud.width
    assert style.block_padding == cfg.hud.block_padding
