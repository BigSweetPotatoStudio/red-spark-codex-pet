from __future__ import annotations

import argparse
import json
import math
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
CELL_WIDTH = 192
CELL_HEIGHT = 208

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


def preserve_jumping_motion_frames() -> None:
    """Keep the source strip's vertical jump arc after component extraction."""
    from PIL import Image

    frame_count = 5
    chroma_key = (255, 0, 255)
    key_threshold = 96.0

    def is_key(red: int, green: int, blue: int) -> bool:
        return math.sqrt(
            (red - chroma_key[0]) ** 2
            + (green - chroma_key[1]) ** 2
            + (blue - chroma_key[2]) ** 2
        ) <= key_threshold

    source_path = ACTION_DIR / "jumping.png"
    with Image.open(source_path) as opened:
        strip = opened.convert("RGBA")

    slot_width = strip.width / frame_count
    sprites: list[dict[str, object]] = []
    for index in range(frame_count):
        left = round(index * slot_width)
        right = round((index + 1) * slot_width)
        slot = strip.crop((left, 0, right, strip.height))
        pixels = slot.load()
        for y in range(slot.height):
            for x in range(slot.width):
                red, green, blue, alpha = pixels[x, y]
                if is_key(red, green, blue):
                    pixels[x, y] = (red, green, blue, 0)
        bbox = slot.getbbox()
        if bbox is None:
            raise SystemExit(f"empty jumping frame slot: {index}")
        sprites.append({"slot": slot, "bbox": bbox})

    max_width = max(sprite["bbox"][2] - sprite["bbox"][0] for sprite in sprites)
    max_height = max(sprite["bbox"][3] - sprite["bbox"][1] for sprite in sprites)
    source_top_min = min(sprite["bbox"][1] for sprite in sprites)
    source_top_max = max(sprite["bbox"][1] for sprite in sprites)
    target_top_min = 5
    target_arc = 50

    scale = min((CELL_WIDTH - 10) / max_width, 1.0)
    if source_top_max > source_top_min:
        for sprite in sprites:
            bbox = sprite["bbox"]
            mapped_top = target_top_min + (
                (bbox[1] - source_top_min) / (source_top_max - source_top_min)
            ) * target_arc
            scale = min(scale, (CELL_HEIGHT - 5 - mapped_top) / (bbox[3] - bbox[1]))
    else:
        scale = min(scale, (CELL_HEIGHT - 10) / max_height)

    state_dir = FRAMES_DIR / "jumping"
    state_dir.mkdir(parents=True, exist_ok=True)
    for index, sprite in enumerate(sprites):
        slot = sprite["slot"]
        bbox = sprite["bbox"]
        cropped = slot.crop(bbox)
        resized = cropped.resize(
            (
                max(1, round(cropped.width * scale)),
                max(1, round(cropped.height * scale)),
            ),
            Image.Resampling.LANCZOS,
        )
        if source_top_max > source_top_min:
            top = round(
                target_top_min
                + ((bbox[1] - source_top_min) / (source_top_max - source_top_min))
                * target_arc
            )
        else:
            top = (CELL_HEIGHT - resized.height) // 2
        left = (CELL_WIDTH - resized.width) // 2
        frame = Image.new("RGBA", (CELL_WIDTH, CELL_HEIGHT), (0, 0, 0, 0))
        frame.alpha_composite(resized, (left, top))
        frame.save(state_dir / f"{index:02d}.png")

    manifest_path = FRAMES_DIR / "frames-manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for row in manifest.get("rows", []):
            if row.get("state") == "jumping":
                row["method"] = "slots-preserve-motion"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


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
    preserve_jumping_motion_frames()
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
