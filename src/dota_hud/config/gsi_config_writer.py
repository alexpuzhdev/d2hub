from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

GSI_REQUIRED_SECTIONS = ["map", "hero", "player", "items"]

GSI_CONFIG_TEMPLATE = '''"Dota HUD" {{
  "uri" "http://127.0.0.1:{port}"
  "timeout" "5.0"
  "buffer" "0.1"
  "throttle" "0.1"
  "heartbeat" "30.0"
  "data" {{
    "map" "1"
    "hero" "1"
    "player" "1"
    "items" "1"
  }}
}}
'''


def write_gsi_config(dota_path: Path, port: int = 4000) -> Path:
    cfg_dir = dota_path / "game" / "dota" / "cfg" / "gamestate_integration"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    cfg_file = cfg_dir / "gamestate_integration_dota_hud.cfg"
    cfg_file.write_text(GSI_CONFIG_TEMPLATE.format(port=port))
    logger.info("GSI config written to %s", cfg_file)
    return cfg_file
