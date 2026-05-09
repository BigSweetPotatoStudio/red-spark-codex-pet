from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACTION_DIR = ROOT / "assets" / "action-sheets"
BUILD_DIR = ROOT / "build"
DECODED_DIR = BUILD_DIR / "decoded"
FRAMES_DIR = BUILD_DIR / "frames"
FINAL_DIR = BUILD_DIR / "final"
QA_DIR = BUILD_DIR / "qa"
PET_DIR = ROOT / "pets" / "red-spark"
PREVIEW_DIR = ROOT / "preview"

STATES = [
    "idle",
    "running-right",
    "running-left",
    "waving",
    "jumping",
    "failed",
    "waiting",
    "running",
    "review",
]


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")


def skill_scripts_dir() -> Path:
    return codex_home() / "skills" / "hatch-pet" / "scripts"


def run(command: list[str]) -> None:
    print("+ " + " ".join(command))
    subprocess.run(command, check=True, cwd=ROOT)


def require_source_images() -> None:
    missing = [state for state in STATES if not (ACTION_DIR / f"{state}.png").exists()]
    if missing:
        raise SystemExit(f"Missing action sheet(s): {', '.join(missing)}")


def prepare_build_dir() -> None:
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    DECODED_DIR.mkdir(parents=True)
    for state in STATES:
        shutil.copy2(ACTION_DIR / f"{state}.png", DECODED_DIR / f"{state}.png")


def copy_preview_outputs() -> None:
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(QA_DIR / "contact-sheet.png", PREVIEW_DIR / "contact-sheet.png")
    shutil.copy2(FINAL_DIR / "validation.json", PREVIEW_DIR / "validation.json")
    review = QA_DIR / "review.json"
    if review.exists():
        shutil.copy2(review, PREVIEW_DIR / "review.json")


def package_pet(scripts: Path) -> None:
    run(
        [
            sys.executable,
            str(scripts / "package_custom_pet.py"),
            "--pet-name",
            "red-spark",
            "--display-name",
            "Red Spark",
            "--description",
            "A red-hatted chibi adventurer companion with a backpack, map, and white mascot bomb.",
            "--spritesheet",
            str(FINAL_DIR / "spritesheet.webp"),
            "--output-dir",
            str(PET_DIR),
            "--force",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build Red Spark by reusing the Codex hatch-pet skill scripts."
    )
    parser.add_argument(
        "--render-videos",
        action="store_true",
        help="Also render MP4 previews if the local video encoder is available.",
    )
    args = parser.parse_args()

    scripts = skill_scripts_dir()
    if not scripts.exists():
        raise SystemExit(f"hatch-pet scripts not found: {scripts}")

    require_source_images()
    prepare_build_dir()
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    QA_DIR.mkdir(parents=True, exist_ok=True)

    run(
        [
            sys.executable,
            str(scripts / "extract_strip_frames.py"),
            "--decoded-dir",
            str(DECODED_DIR),
            "--output-dir",
            str(FRAMES_DIR),
            "--states",
            "all",
            "--chroma-key",
            "#FF00FF",
            "--method",
            "auto",
        ]
    )
    run(
        [
            sys.executable,
            str(scripts / "inspect_frames.py"),
            "--frames-root",
            str(FRAMES_DIR),
            "--json-out",
            str(QA_DIR / "review.json"),
        ]
    )
    run(
        [
            sys.executable,
            str(scripts / "compose_atlas.py"),
            "--frames-root",
            str(FRAMES_DIR),
            "--output",
            str(FINAL_DIR / "spritesheet.png"),
            "--webp-output",
            str(FINAL_DIR / "spritesheet.webp"),
        ]
    )
    run(
        [
            sys.executable,
            str(scripts / "validate_atlas.py"),
            str(FINAL_DIR / "spritesheet.webp"),
            "--json-out",
            str(FINAL_DIR / "validation.json"),
        ]
    )
    run(
        [
            sys.executable,
            str(scripts / "make_contact_sheet.py"),
            str(FINAL_DIR / "spritesheet.webp"),
            "--output",
            str(QA_DIR / "contact-sheet.png"),
        ]
    )

    if args.render_videos:
        run(
            [
                sys.executable,
                str(scripts / "render_animation_videos.py"),
                str(FINAL_DIR / "spritesheet.webp"),
                "--output-dir",
                str(QA_DIR / "videos"),
            ]
        )

    package_pet(scripts)
    copy_preview_outputs()

    validation = json.loads((FINAL_DIR / "validation.json").read_text(encoding="utf-8"))
    review = json.loads((QA_DIR / "review.json").read_text(encoding="utf-8"))
    if validation.get("errors") or review.get("errors"):
        print("Build completed with validation errors. See preview/validation.json and preview/review.json.")
        return 1

    print(f"Built pet package: {PET_DIR}")
    print(f"Preview contact sheet: {PREVIEW_DIR / 'contact-sheet.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
