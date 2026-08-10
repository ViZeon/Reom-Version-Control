# Roadmap & TODOs

## Completed Phases
*   **Phase 0: Bug Squashing:** Fixed asset duplication, catalog creation, and auto-refresh logic.
*   **Phase 1: UI/UX Polish:** Implemented empty states, human-readable version formats (`v1.0.1`), and logical button flow.
*   **Phase 2: Version Math:** Added `Step` and `Release` actions via a unified operator with an EnumProperty.
*   **Phase 3: Edit Mode Flow:** Implemented `Enter Edit` (make local) and `End Edit` (save, delete, re-link).
*   **Phase 4: Keymaps:** Added `Ctrl+W` for saving, fully registered in Blender's keymap preferences.
*   **Phase 5: Storage Modes:** Implemented Per-Current, Per-Sub, and Per-Release packing with automated migration and snapshot backups.
*   **Phase 6: Architecture Overhaul:** Modularized codebase into a Python package, added UUID identity system, and implemented the Universal Safe Write Gateway.
*   **Phase 7: Testing & Logging:** Added `logger.py` and `tests.py` with integration tests for Blender file I/O.

---

## Upcoming Features (Project TODOs)

### 1. UI List Refactor & Dual Highlighting
**Current State:** Versions are displayed in a basic `box.row()` layout with a button next to each label.
**Target:** Refactor into a standard Blender `UIList`.
*   **Active State Indicator:** The version currently being edited (if applicable) needs a visual indicator in the list.
*   **Main State Indicator:** The version currently published as the main asset in the library needs a distinct visual indicator (e.g., a specific icon or active state) so the user knows what the library is currently serving.

### 2. Hover Preview
**Target:** Add a togglable preference to preview versions in the 3D scene on hover.
*   When hovering over a version in the UI list, import a temporary, renamed copy of that version into the scene.
*   Enable X-ray shading for the temporary object.
*   Apply a distinct color overlay to visually separate it from the live scene.
*   Remove the temporary object when the mouse leaves the list item.

### 3. Rollback / Branching
**Current State:** `Set Main` extracts an older version to the library, but the user has to manually click `Enter Edit` on the live object to start modifying it.
**Target:** Add a "Rollback to Edit" action.
*   Loads the selected older version directly into the scene as an active (local) working copy.
*   Modifies the version math so the next save continues *from* that older version number, effectively branching the timeline forward from the past state.

### 4. Duplicate Detection
**Current State:** If the user sets up a new object and names it `Cube`, and a `Cube.blend` already exists in the target directory, the addon will just overwrite it (or backup it).
**Target:** Add an intelligent prompt.
*   If the user clicks `Setup Lib File` and enters a name that matches an existing library file, show a dialog: *"An asset named 'Cube' already exists. Do you want to link to this existing asset, or create a new one?"*
*   This prevents users from accidentally creating duplicate entries for the same asset.

### 5. Auto-Highlight / Auto-Set Main
**Current State:** Saving always overwrites the library file with the newest version.
**Target:** Add a preference toggle for "Auto-Set Main".
*   If enabled (default), saving a new version automatically sets it as the main asset in the library, updating the Asset Browser instantly.
*   If disabled, saving just writes the backup to `_versions/`, and the library file retains the *previous* main version until the user manually clicks `Set Main`.