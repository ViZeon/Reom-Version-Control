"""Pure functions and business logic. No operator classes. No bpy calls."""

import os
import sys
import shutil
from . import blender_api
from .variables import (
    FIRST_RUN_DELAY, VERSIONS_FOLDER_NAME,
    MESH_PROP_NAME, MESH_PROP_VERSION, MESH_PROP_LIB_FILE, MESH_PROP_TAG,
    DEFAULT_TAGS,
)
from .variables_ui import STARTUP_BL_IDNAME

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
    name = blender_api.object_get_property(obj, MESH_PROP_NAME)
    if name is None:
        name = obj.name
    return name

def mesh_set_name(obj, name):
    blender_api.object_set_property(obj, MESH_PROP_NAME, name)

def mesh_get_version(obj):
    ver_str = blender_api.object_get_property(obj, MESH_PROP_VERSION)
    if ver_str:
        return version_from_string(ver_str)
    return None

def mesh_set_version(obj, ver_tuple):
    blender_api.object_set_property(obj, MESH_PROP_VERSION, version_to_string(ver_tuple))

def mesh_get_lib_file(obj):
    return blender_api.object_get_property(obj, MESH_PROP_LIB_FILE)

def mesh_set_lib_file(obj, filepath):
    blender_api.object_set_property(obj, MESH_PROP_LIB_FILE, filepath)

def mesh_get_tag(obj):
    return blender_api.object_get_property(obj, MESH_PROP_TAG)

def mesh_set_tag(obj, tag):
    blender_api.object_set_property(obj, MESH_PROP_TAG, tag)

# === TAG SYSTEM ===

def tag_list_parse(tags_string):
    if not tags_string:
        return []
    return [t.strip() for t in tags_string.split(',') if t.strip()]

def tag_list_join(tags_list):
    return ', '.join(tags_list)

def tag_to_catalog(tag):
    return str(hash(tag) % (2**31))

# === VERSION MATH ===

def version_bump_current(v):
    return (v[0], v[1], v[2] + 1)

def version_from_string(s):
    parts = s.split('_')
    return tuple(int(p) for p in parts)

def version_to_string(v):
    return '_'.join(str(n) for n in v)

# === FILE PATH ===

def file_scan_versions(mesh_name, lib_path):
    versions = []
    lib_path = file_find_library_root(lib_path)
    if not lib_path:
        return versions
    
    versions_folder = os.path.join(lib_path, VERSIONS_FOLDER_NAME, mesh_name)
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
    if not lib_path:
        return None
    
    lib_path = os.path.expanduser(lib_path)
    
    if os.path.exists(os.path.join(lib_path, VERSIONS_FOLDER_NAME)):
        return lib_path
    
    try:
        for name in os.listdir(lib_path):
            sub = os.path.join(lib_path, name)
            if os.path.isdir(sub) and os.path.exists(os.path.join(sub, VERSIONS_FOLDER_NAME)):
                return sub
    except:
        pass
    
    return None

def file_ensure_versions_folder(mesh_name, lib_root):
    folder = os.path.join(lib_root, VERSIONS_FOLDER_NAME, mesh_name)
    os.makedirs(folder, exist_ok=True)

def file_build_version_path(mesh_name, ver_str, lib_root):
    folder = os.path.join(lib_root, VERSIONS_FOLDER_NAME, mesh_name)
    filename = f"{mesh_name}_{ver_str}.blend"
    return os.path.join(folder, filename)

# === LIBRARY FILE OPERATIONS ===

def library_write_object(obj, filepath):
    """Save object and its data blocks to a .blend file. Plain file, no asset setup."""
    blocks = {obj}
    if obj.data:
        blocks.add(obj.data)
    for mat in obj.data.materials:
        if mat:
            blocks.add(mat)
    blender_api.data_libraries_write(filepath, blocks, fake_user=True)

def tag_to_catalog(tag):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, tag))

def library_update_from_object(obj, lib_filepath, tag):
    """Mark asset on original object, write clean file. No load/writeback."""
    if not obj.asset_data:
        blender_api.asset_mark(obj)
    if tag and obj.asset_data:
        blender_api.asset_set_catalog(obj, tag_to_catalog(tag))
    library_write_object(obj, lib_filepath)

def library_update_from_file(source_path, lib_filepath, tag):
    """Load backup, mark asset, write ONE object to library, cleanup."""
    existing = set(bpy.data.objects.keys())
    
    with blender_api.libraries_load(source_path, link=False) as (data_from, data_to):
        data_to.objects = data_from.objects
    
    loaded = [ob for ob in bpy.data.objects if ob.name not in existing]
    
    for ob in loaded:
        if not ob.asset_data:
            blender_api.asset_mark(ob)
        if tag and ob.asset_data:
            blender_api.asset_set_catalog(ob, tag_to_catalog(tag))
        library_write_object(ob, lib_filepath)
        blender_api.object_remove(ob)