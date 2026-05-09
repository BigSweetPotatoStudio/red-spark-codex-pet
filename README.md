# Red Spark Codex Pet

Red Spark is a custom animated Codex pet: a red-hatted chibi adventurer with a backpack, map, and white mascot bomb.

![Red Spark contact sheet](preview/contact-sheet.png)

## Install

Copy the pet folder into your Codex pets directory:

```powershell
Copy-Item -Recurse -Force .\pets\red-spark "$env:USERPROFILE\.codex\pets\red-spark"
```

Then restart Codex or reload the pet list.

## Files

- `pets/red-spark/pet.json`: pet manifest.
- `pets/red-spark/spritesheet.webp`: 1536x1872 RGBA sprite atlas.
- `preview/contact-sheet.png`: QA contact sheet showing all animation states.
- `preview/validation.json`: atlas validation output.

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
