# Project Guidance

This repository packages the Red Spark custom Codex pet.

## Important Paths

- `assets/action-sheets/`: editable source strips, one PNG per pet state.
- `docs/hatch-pet-skill.md`: reference copy of the `hatch-pet` skill page.
- `pets/red-spark/`: installable Codex pet package.
- `preview/contact-sheet.png`: generated QA sheet.
- `scripts/build.py`: rebuilds the atlas and package from action sheets by reusing the local Codex `hatch-pet` skill scripts.
- `scripts/install.ps1`: installs the package into a local Codex home.

## Build Contract

The pet atlas is fixed at `1536x1872`, with `8` columns, `9` rows, and `192x208` cells.

State order and frame counts:

1. `idle`: 6
2. `running-right`: 8
3. `running-left`: 8
4. `waving`: 4
5. `jumping`: 5
6. `failed`: 8
7. `waiting`: 6
8. `running`: 6
9. `review`: 6

Do not change these counts unless you also update `scripts/build.py` and verify the Codex app accepts the new layout.

## Editing Workflow

When changing one animation, edit only the matching file under `assets/action-sheets/`.
Keep the magenta background removable and keep each pose inside its invisible frame slot.
After editing, run:

```powershell
.\scripts\build.ps1
```

Then inspect `preview/contact-sheet.png`, `preview/validation.json`, and `preview/review.json`.

Do not reimplement frame extraction, atlas composition, or validation in this repository unless the upstream `hatch-pet` scripts are unavailable. Use `docs/hatch-pet-skill.md` as the local reference page, and prefer calling:

- `extract_strip_frames.py`
- `inspect_frames.py`
- `compose_atlas.py`
- `validate_atlas.py`
- `make_contact_sheet.py`
- `package_custom_pet.py`

For this editable-source repository, do not pass `--require-components` to `inspect_frames.py`.
Generated action strips can legitimately fall back to slot slicing after manual edits; the acceptance check is the final contact sheet plus atlas validation.

## Visual Constraints

- Keep Red Spark recognizable: red cap, pale hair, red outfit, backpack, mascot charm.
- Avoid text, UI, labels, frame numbers, shadows, glow, dust, speed lines, and detached effects.
- Keep props close to the body so frame extraction stays stable.
- The `running` row means in-progress work, not directional travel.
