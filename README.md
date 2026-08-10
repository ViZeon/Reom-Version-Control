# Reom Version Control

Lean, modular version control for Blender assets. Save iterations, pack versions, and manage linked assets without leaving the 3D view.

## Installation

1. Download `reom_version_control` as a `.zip` file.
2. In Blender, go to `Edit > Preferences > Add-ons > Install...`.
3. Select the `.zip` file and enable `Reom Version Control`.
4. Open the N-Panel (press `N`) in the 3D Viewport. Find the **Reom VC** tab.

## Quick Start

1. Select a mesh object.
2. Click **Setup Lib File**. Choose an Asset Name and a target `.blend` file.
3. Click **Set Category**. Pick an existing Asset Browser catalog or create a new one.
4. Edit your mesh.
5. Click **Save** (or press `Ctrl+W`).

## Core Workflow

### 1. Setup & Identity
The addon binds the object to a `.blend` library file using a persistent UUID and a user-chosen Asset Name. You can rename the object in the scene to `Cube.001` or `TrashBag`, and the addon will always know its true identity.

### 2. Edit Mode Flow
* **Linked (Read-Only):** Drag an asset from the Asset Browser. It is safe from accidental edits.
* **Enter Edit:** Click to make the object local and fully editable.
* **End Edit:** Saves the final version, deletes the local object, and re-links the clean asset from the library.

### 3. Version Math
| Action | Math | Result |
|--------|------|--------|
| **Save** | current += 1 | `v0.0.1` → `v0.0.2` |
| **Step** | sub += 1, current = 0 | `v0.0.5` → `v0.1.0` |
| **Release** | release += 1, sub = 0, current = 0 | `v1.9.9` → `v2.0.0` |

### 4. Set Main (Rollback)
Click **Set Main** next to any older version in the UI list. The addon extracts that specific version and makes it the active asset in the library.

## Storage Modes

Configure how version backups are stored in the Addon Preferences. Switching modes automatically migrates existing files and takes a snapshot backup.

* **Per-Current:** Every save creates a new file (`Cube_0_0_1.blend`).
* **Per-Sub (Default):** Packs all saves of a sub-version into one file (`Cube_0_0.versions.blend`).
* **Per-Release:** Packs all saves of a release into one file (`Cube_0.versions.blend`).

*Note: Packed files maintain 1 rolling backup in a `_backup_{mode}/` folder.*

## Keymaps

* **Ctrl+W**: Save Version

## Architecture (For Developers)

Built on a strict 4-layer architecture. Zero hardcoded data outside `data/`. Zero `bpy` calls outside `wrapper/`. 

* `data/`: Constants and UI strings.
* `wrapper/`: 1-liner `bpy` adapters.
* `functions/`: Pure business logic. No Blender API calls.
* `ui/`: Dumb operators and panels. Calls `functions/` only.

All file writes route through a Safe Write Gateway to prevent data loss. Unit tests included.