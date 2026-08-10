

Read this, and you will know exactly where every line of code belongs.

### The 4 Golden Rules
1. **No data in functions.** No hardcoded strings, paths, or enums.
2. **No logic in data.** Just constants. If it has parentheses, it doesn't belong here.
3. **No `bpy` in functions.** Blender calls live *only* in the wrapper.
4. **No OOP outside UI.** Operators and Panels are forced OOP. Keep them dumb. They draw boxes and trigger actions.

---

### The Layers

**1. `data.py` (The Dictionary)**
* **Role:** Single source of truth. Pure data.
* **Format:** `UPPER_SNAKE_CASE`. Grouped by domain (`# === UI ===`, `# === PROPERTIES ===`).
* **Rule:** Prefixes make indexing instant (`OP_` for operators, `P_` for properties, `TEXT_` for UI strings).

**2. `wrapper.py` (The Translator)**
* **Role:** 1-liner adapters. Translates our plain Python into `bpy` calls.
* **Format:** `snake_case`. Verbs only (`get_`, `set_`, `invoke_`).
* **Rule:** Zero math. Zero business logic. If it needs a loop, the loop goes in `functions.py`.

**3. `functions.py` (The Brain)**
* **Role:** Pure logic. Data in, data out.
* **Format:** `snake_case`. Verbs for actions (`save_version`), nouns for queries (`scan_info`).
* **Rule:** Never imports `bpy`. Never hardcodes a string. Calls `wrapper` for Blender access.

**4. `ui_operators.py` & `ui_panels.py` (The Face)**
* **Role:** Blender-forced OOP. Draws UI and captures clicks.
* **Format:** `REOM_VC_OT_name` (Operators), `REOM_VC_PT_name` (Panels).
* **Rule:** The UI is blind and dumb. It grabs the active object, passes it to a `functions.action()`, and reports the string it gets back. No path building, no version math, no file scanning logic.

**5. `registry.py` (The Usher)**
* **Role:** Imports UI classes and orders them for registration.
* **Format:** Single `classes` tuple.

---

### Naming Conventions (ELI5 & Index Friendly)

Because of strict prefixes, you can type `data.OP_` or `data.TEXT_` and your IDE will show you exactly what you need.

| Domain | Prefix | Example | Used By |
|---|---|---|---|
| Operators | `OP_` | `OP_SAVE = "reom_vc.save"` | UI, Wrapper invoke |
| Properties| `P_` | `P_VER = "reom_vc_ver"` | Functions, Wrapper |
| UI Text | `TEXT_` | `TEXT_MESH = "Mesh: "` | UI Panels/Operators |
| Errors | `ERR_` | `ERR_NO_OBJ = "..."` | UI Operators |
| Enums | `AREA_` / `REGION_`| `AREA_VIEW3D = 'VIEW_3D'` | UI Panels, Wrapper |

---

### Workflow: How to add a new feature

Let's say you want to add a "Force Save" button that bypasses version bumping.

**1. `data.py` (Add the data)**
```python
OP_FORCE = "reom_vc.force_save"
TEXT_FORCE = "Force Save"
```

**2. `wrapper.py` (No changes needed)**
*We already have `write_lib` and `get_active_obj`.*

**3. `functions.py` (Add the logic)**
```python
def force_save(obj):
    lib = get_lib(obj)
    if not lib: return data.ERR_NO_LIB
    write_obj(obj, lib)
    return f"Forced {get_name(obj)} to lib"
```

**4. `ui_operators.py` (Add the dumb button)**
```python
class REOM_VC_OT_force(bpy.types.Operator):
    bl_idname = data.OP_FORCE
    bl_label = data.TEXT_FORCE
    def execute(self, ctx):
        obj = wrapper.get_active_obj()
        if not obj: return _report(self, data.ERR_NO_OBJ)
        return _report(self, functions.force_save(obj), data.REPORT_INFO)
```

**5. `registry.py` (Register it)**
```python
from .ui_operators import REOM_VC_OT_force
# Add to classes tuple
```

**6. `ui_panels.py` (Draw it)**
```python
l.operator(data.OP_FORCE)
```

---

### Documentation Rules (The "Lean & ELI5" Standard)

When writing docstrings, readmes, or dev docs for this codebase, adhere strictly to these rules:

1. **Maximum Lexical Density:** Zero fluff. No "This function is responsible for...". Just say what it is. `"""Save object and data blocks to a .blend file."""` 
2. **ELI5, but Technical:** Explain the *what* and *why* in plain English, but assume the reader knows basic programming terms (adapters, pure functions, blocks). A newcomer should instantly understand the intent without reading the code.
3. **Action-Oriented:** Start descriptions with verbs. `Save`, `Load`, `Bump`, `Sync`.
4. **No Stating the Obvious:** Don't document that a function returns a string if the function is named `get_string`. Only document non-obvious side effects (e.g., "Deletes original objects after load").
5. **File Headers:** Every file gets a 1-line docstring defining its architectural role and the rules it obeys.
   * `"""Thin Blender API adapters. No logic."""` (wrapper.py)
   * `"""Pure functions and business logic. No bpy. No hardcoded constants."""` (functions.py)
   * `"""UI logic for Operators. No business logic."""` (ui_operators.py)
6. **Example Formats:** When showing how to add a feature, use the raw, dense format. Show the file name, the exact snippet, and move on. No long-winded explanations between code blocks.