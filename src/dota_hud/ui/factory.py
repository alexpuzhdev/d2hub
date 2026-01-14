from __future__ import annotations

from ..application.hud_port import HudPort
from ..config.models import HudConfig
from .hud_style import HudStyle


class UiFactory:
    """Создаёт HUD окно на основе конфигурации."""

    def build(self, config: HudConfig) -> HudPort:
        """Создаёт реализацию HUD по имени UI."""
        ui_name = (config.ui or "qt").lower()
        style = HudStyle(
            title=config.title,
            width=config.width,
            height=config.height,
            x=config.x,
            y=config.y,
            alpha=config.alpha,
            font_family=config.font_family,
            font_size=config.font_size,
            font_weight=config.font_weight,
        )

        if ui_name == "qt":
            from .qt.hud_window import HudQt

            return HudQt(style)

        raise ValueError(f"Unsupported HUD UI backend: {ui_name}")
