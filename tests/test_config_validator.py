from __future__ import annotations

import tempfile
from pathlib import Path
from dota_hud.config.validator import validate_gsi_config, ValidationResult
from dota_hud.config.gsi_config_writer import write_gsi_config, GSI_REQUIRED_SECTIONS


def test_validation_result_ok():
    r = ValidationResult(ok=True, errors=[])
    assert r.ok

def test_validation_missing_file():
    r = validate_gsi_config(Path("/nonexistent/path/cfg"))
    assert not r.ok

def test_write_and_validate():
    with tempfile.TemporaryDirectory() as tmpdir:
        dota_path = Path(tmpdir)
        write_gsi_config(dota_path)
        cfg_dir = dota_path / "game" / "dota" / "cfg"
        r = validate_gsi_config(cfg_dir)
        assert r.ok

def test_validation_missing_sections():
    with tempfile.TemporaryDirectory() as tmpdir:
        cfg_dir = Path(tmpdir) / "cfg" / "gamestate_integration"
        cfg_dir.mkdir(parents=True)
        cfg_file = cfg_dir / "gamestate_integration_dota_hud.cfg"
        cfg_file.write_text('"Dota HUD" { "uri" "http://127.0.0.1:4000" "data" { "map" "1" } }')
        r = validate_gsi_config(Path(tmpdir) / "cfg")
        assert not r.ok

def test_required_sections_list():
    assert "map" in GSI_REQUIRED_SECTIONS
    assert "hero" in GSI_REQUIRED_SECTIONS
