from __future__ import annotations

import sys
from pathlib import Path

from .app import run_app


def main() -> None:
    """Точка входа CLI для запуска HUD."""
    project_root = Path(__file__).resolve().parents[2]
    default_config = project_root / "configs" / "timings.yaml"

    config_path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else default_config
    run_app(config_path)


if __name__ == "__main__":
    main()
