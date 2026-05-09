from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PET_ID = "red-spark"
SOURCE_DIR = ROOT / "pets" / PET_ID


def default_codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".codex"


def copy_package(source: Path, destination: Path) -> None:
    if not source.is_dir():
        raise SystemExit(f"Pet package not found: {source}. Run scripts/build.py first.")
    for required in ("pet.json", "spritesheet.webp"):
        if not (source / required).is_file():
            raise SystemExit(f"Pet package is missing {required}: {source}")

    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Red Spark into a local Codex home.")
    parser.add_argument(
        "--codex-home",
        type=Path,
        default=default_codex_home(),
        help="Codex home directory. Defaults to CODEX_HOME or ~/.codex.",
    )
    args = parser.parse_args()

    destination = args.codex_home.expanduser() / "pets" / PET_ID
    copy_package(SOURCE_DIR, destination)
    print(f"Installed Red Spark to {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
