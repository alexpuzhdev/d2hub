from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

REQUIRED_SECTIONS = ["map", "hero", "player", "items"]


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str] = field(default_factory=list)


def validate_gsi_config(cfg_dir: Path) -> ValidationResult:
    errors: list[str] = []
    gsi_dir = cfg_dir / "gamestate_integration" if cfg_dir.name != "gamestate_integration" else cfg_dir
    cfg_file = gsi_dir / "gamestate_integration_dota_hud.cfg"
    if not cfg_file.exists():
        return ValidationResult(ok=False, errors=[f"GSI config not found: {cfg_file}"])
    content = cfg_file.read_text()
    for section in REQUIRED_SECTIONS:
        if f'"{section}" "1"' not in content:
            errors.append(f"Missing GSI section: {section}")
    if '"uri"' not in content:
        errors.append("Missing URI in GSI config")
    return ValidationResult(ok=len(errors) == 0, errors=errors)


def validate_yaml_configs(config_path: Path) -> ValidationResult:
    errors: list[str] = []
    if not config_path.exists():
        return ValidationResult(ok=False, errors=[f"Config not found: {config_path}"])
    try:
        from .loader import load_config
        load_config(config_path)
    except Exception as e:
        errors.append(f"Config parse error: {e}")
    return ValidationResult(ok=len(errors) == 0, errors=errors)
