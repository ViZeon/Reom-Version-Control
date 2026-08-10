Here is the updated Code Guide. It reflects the fully modularized folder structure, the new identity system, the safe write gateway, and the storage modes. It is written for maximum lexical density—zero fluff, pure signal.

---

# Reom Addon Dev Docs

## Architecture

Modular, 4-layer package architecture. Zero hardcoded data outside `data/`.

| Package / File | Role | Rules |
|------|------|-------|
| `data/` | Constants, UI strings, enums. | No functions. No logic. |
| `wrapper/` | 1-liner `bpy` adapters. | No logic. Just translates calls. |
| `functions/` | Pure business logic. | No `bpy`. No hardcoded data. |
| `ui/` | Blender Operator & Panel classes. | Calls `functions/`. Dumb UI. |
| `utils/` | Logging and Unit Tests. | Standard Python libraries. |

### `functions/` Sub-modules
To keep files bite-sized and indexable, `functions/` is split into:
* `lifecycle.py`: Addon register/unregister, keymaps, startup timer.
* `state.py`: Getters/Setters for object properties (UUID, Name, Ver, Lib).
* `math.py`: Version bumping and UI string formatting.
* `paths.py`: Directory scanning, path building, and Storage Mode migration.
* `gateway.py`: The universal `safe_write` function and conflict resolvers.
* `categories.py`: Reading/writing `blender_assets.cats.txt`.
* `sync.py`: Library validation, writing objects, packing versions, syncing to lib.
* `actions.py`: High-level actions called by UI (e.g., `save_version`, `set_main_version`).

## The 4 Golden Rules
1. **No data in functions.** No hardcoded strings, paths, or enums.
2. **No logic in data.** Just constants. If it has parentheses, it doesn't belong here.
3. **No `bpy` in functions.** Blender calls live *only* in `wrapper/`.
4. **No OOP outside UI.** Operators and Panels are forced OOP. Keep them dumb.

## Identity System
We do not rely on Blender object names (`Cube.001` happens constantly).
* `P_NAME`: The user-chosen asset name (locked in at setup).
* `P_UUID`: A unique ID injected into the object. Inherited by appended/duplicated objects.
* Library files are named `{P_NAME}.blend`.

## Storage Modes
Version backups are stored in `/_versions/{P_NAME}/`.
* `MODE_VER`: Individual files per save (`Cube_1_0_0.blend`).
* `MODE_SUB`: Packed files per sub-version (`Cube_1_0.versions.blend`).
* `MODE_RELEASE`: Packed files per release (`Cube_1.versions.blend`).

**Migration:** Changing modes in preferences triggers `migrate_all_versions`. It unpacks all packed files to individual files, takes a snapshot backup in `/_backup_migration/`, then repacks them according to the new mode.

## The Safe Write Gateway
ALL file writes MUST go through `functions.gateway.safe_write(path, file_data, mode)`.
* `MODE_SAFE`: Appends `_1` if file exists.
* `MODE_REPLACE`: Deletes old file, writes new.
* `MODE_BACKUP`: Moves old file to `/_backup_{mode}/`.
* `MODE_CUSTOM`: Pass custom resolver functions.

## How to Add a New Operator
1. Add `OP_NAME` and `TEXT_NAME` to `data/__init__.py`.
2. Write the logic in `functions/actions.py` (e.g., `def do_thing(obj): ...`).
3. Write the class in `ui/operators.py`. Call `functions.do_thing()`. Report the result.
4. Import in `ui/registry.py`, add to `classes` tuple.
5. Add a button in `ui/panels.py` via `l.operator(data.OP_NAME)`.

## Version System
Format: `release_sub_current` (e.g., `0_0_0`). Starts at `0_0_0`.

| Action | Math | UI Display |
|--------|------|------|
| Save | current += 1 | `v0.0.1` |
| Step | sub += 1, current = 0 | `v0.1.0` |
| Release | release += 1, sub = 0, current = 0 | `v1.0.0` |

**Set Main:** Extracts a specific version from the versions folder, writes it to `Cube.blend` (replacing the main asset), and re-links the object in the scene.

## Edit Mode Flow
1. **Linked (Read-Only):** Object is linked from `Cube.blend`.
2. **Enter Edit:** Calls `make_local()`. Object is now fully editable.
3. **Save:** Bumps version, packs backup, overwrites `Cube.blend`.
4. **End Edit:** Saves final version, deletes local object, re-links from `Cube.blend`.

## Testing & Logging
* **Logging:** `utils/logger.py` writes to `reom_vc.log` in Blender's temp directory.
* **Unit Tests:** `utils/tests.py` contains standard `unittest` suites for math, paths, and the safe write gateway. Run via the "Run Unit Tests" operator in the Reom VC panel.