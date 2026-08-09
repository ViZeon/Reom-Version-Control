"""Operator classes + all business logic. Organized by prefix regions."""

import os
import sys
import bpy
from . import blender_api
from .variables import FIRST_RUN_DELAY, VERSIONS_FOLDER_NAME, MESH_PROP_NAME, MESH_PROP_VERSION
from .variables_ui import STARTUP_BL_IDNAME, STARTUP_LABEL, STARTUP_TEXT

# === OPERATOR CLASSES ===

class REOM_VC_OT_startup(bpy.types.Operator):
    bl_idname = STARTUP_BL_IDNAME
    bl_label = STARTUP_LABEL
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)
    
    def draw(self, context):
        self.layout.label(text=STARTUP_TEXT)
        prefs = context.preferences.addons[__package__].preferences
        self.layout.prop(prefs, "lib_path")
    
    def execute(self, context):
        return {'FINISHED'}

# === ADDON LIFECYCLE ===

def addon_register(class_list):
    blender_api.classes_register(class_list)
    
    mod = sys.modules.get(__package__)
    auto_enabled = mod and getattr(mod, "_AUTO_ENABLED_BY_REOM_EXT", False)
    
    if auto_enabled:
        setattr(mod, "_AUTO_ENABLED_BY_REOM_EXT", False)
    else:
        def _startup():
            window, area = blender_api.context_get_view3d_area()
            if window and area:
                with blender_api.context_temp_override(window, area):
                    blender_api.operator_invoke(STARTUP_BL_IDNAME)
            return None
        blender_api.timer_register(_startup, FIRST_RUN_DELAY)

def addon_unregister(class_list):
    blender_api.classes_unregister(class_list)

# === MESH IDENTITY ===

def mesh_get_name(obj):
    """Read mesh identity from object. Falls back to object name."""
    name = blender_api.object_get_property(obj, MESH_PROP_NAME)
    if name is None:
        name = obj.name
    return name

def mesh_set_name(obj, name):
    """Write mesh identity to object."""
    blender_api.object_set_property(obj, MESH_PROP_NAME, name)

def mesh_get_version(obj):
    """Read version tuple from object. Returns None if not set."""
    ver_str = blender_api.object_get_property(obj, MESH_PROP_VERSION)
    if ver_str:
        return version_from_string(ver_str)
    return None

def mesh_set_version(obj, ver_tuple):
    """Write version tuple to object."""
    blender_api.object_set_property(obj, MESH_PROP_VERSION, version_to_string(ver_tuple))

# === VERSION MATH ===

def version_from_string(s):
    """'1_0_5' → (1, 0, 5). Raises ValueError on bad input."""
    parts = s.split('_')
    return tuple(int(p) for p in parts)

def version_to_string(v):
    """(1, 0, 5) → '1_0_5'."""
    return '_'.join(str(n) for n in v)

# === FILE SCANNING ===

def file_scan_versions(mesh_name, lib_path):
    versions = []
    
    lib_path = file_find_library_root(lib_path)
    if not lib_path:
        return versions
    
    versions_folder = os.path.join(lib_path, VERSIONS_FOLDER_NAME)
    if not os.path.exists(versions_folder):
        return versions
    
    prefix = mesh_name + '_'
    suffix = '.blend'
    
    for filename in os.listdir(versions_folder):
        if filename.startswith(prefix) and filename.endswith(suffix):
            ver_part = filename[len(prefix):-len(suffix)]
            try:
                versions.append(version_from_string(ver_part))
            except ValueError:
                continue
    return versions

def file_find_library_root(lib_path):
    """If lib_path has no _versions/, scan one level deep for a subfolder that does."""
    if not lib_path:
        return None
    
    lib_path = os.path.expanduser(lib_path)
    
    # Direct hit
    if os.path.exists(os.path.join(lib_path, VERSIONS_FOLDER_NAME)):
        return lib_path
    
    # Scan subfolders
    try:
        for name in os.listdir(lib_path):
            sub = os.path.join(lib_path, name)
            if os.path.isdir(sub) and os.path.exists(os.path.join(sub, VERSIONS_FOLDER_NAME)):
                return sub
    except:
        pass
    
    return None