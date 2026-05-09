# Red Spark Codex Pet

Red Spark is a custom animated Codex pet: a red-hatted chibi adventurer with a backpack, map, and white mascot bomb.

![Red Spark contact sheet](preview/contact-sheet.png)

## Install

From this repository:

```powershell
.\scripts\install.ps1
```

Or copy the pet folder manually into your Codex pets directory:

```powershell
Copy-Item -Recurse -Force .\pets\red-spark "$env:USERPROFILE\.codex\pets\red-spark"
```

Then restart Codex or reload the pet list.

## Edit And Rebuild

The editable source images live in `assets/action-sheets/`.

To change one animation, edit the matching PNG, for example:

```text
assets/action-sheets/running.png
```

Then rebuild the installable pet package:

```powershell
.\scripts\build.ps1
```

The build script reuses the local Codex `hatch-pet` skill scripts and regenerates:

- `pets/red-spark/pet.json`
- `pets/red-spark/spritesheet.webp`
- `preview/contact-sheet.png`
- `preview/validation.json`
- `preview/review.json`

After rebuilding, run the install script again:

```powershell
.\scripts\install.ps1
```

## Build Requirements

- Python 3.10 or newer.
- Pillow.
- A local Codex install with the `hatch-pet` skill available at:

```text
%USERPROFILE%\.codex\skills\hatch-pet
```

Install Pillow if needed:

```powershell
python -m pip install -r requirements.txt
```

## Files

- `assets/action-sheets/*.png`: editable action strip sources.
- `pets/red-spark/pet.json`: pet manifest.
- `pets/red-spark/spritesheet.webp`: 1536x1872 RGBA sprite atlas.
- `preview/contact-sheet.png`: QA contact sheet showing all animation states.
- `preview/validation.json`: atlas validation output.
- `preview/review.json`: frame extraction and component QA output.
- `scripts/build.ps1`: rebuild package from source action strips.
- `scripts/install.ps1`: install to the local Codex pets directory.
- `AGENTS.md`: project guidance for future Codex work.

## Animation States

- `idle`: energetic idle loop.
- `running-right`: rightward run.
- `running-left`: leftward run.
- `waving`: cheerful greeting.
- `jumping`: happy jump.
- `failed`: small failure reaction.
- `waiting`: patient waiting loop.
- `running`: in-progress action with a white mascot bomb.
- `review`: checking a small map from the backpack.

## Notes

The final atlas validates as `1536x1872`, `RGBA`, with no validation errors or warnings.
