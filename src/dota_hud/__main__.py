from __future__ import annotations

import sys
from pathlib import Path

from .app import run_app


def main() -> None:
    # По умолчанию ищем configs/timings.yaml рядом с проектом
    project_root = Path(__file__).resolve().parents[2]
    default_cfg = project_root / "configs" / "timings.yaml"

    cfg_path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else default_cfg
    run_app(cfg_path)


if __name__ == "__main__":
    main()
