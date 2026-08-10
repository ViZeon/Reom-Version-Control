"""Pure functions and business logic. No bpy calls."""

import os
import sys
import uuid
from . import wrapper
from . import data

# === ADDON LIFECYCLE ===
def addon_register(class_list):
    wrapper.register_classes(class_list)
    mod = sys.modules.get(__package__)
    if mod and getattr(mod, data.AUTO_ENABLE_FLAG, False):
        setattr(mod, data.AUTO_ENABLE_FLAG, False)
    else:
        def _startup():
            win, area = wrapper.get_view3d_context()
            if win and area:
                with wrapper.temp_override(win, area):
                    wrapper.invoke_operator(data.OP_STARTUP_ID)
        wrapper.register_timer(_startup, data.FIRST_RUN_DELAY)

def addon_unregister(class_list):
    wrapper.unregister_classes(class_list)

# === MESH STATE ===
def mesh_get_name(obj):
    return wrapper.get_property(obj, data.PROP_MESH_NAME) or obj.name

def mesh_get_version(obj):
    v = wrapper.get_property(obj, data.PROP_MESH_VERSION)
    return version_from_string(v) if v else None

def mesh_set_version(obj, ver_tuple):
    wrapper.set_property(obj, data.PROP_MESH_VERSION, version_to_string(ver_tuple))

def mesh_get_lib_file(obj):
    return wrapper.get_property(obj, data.PROP_MESH_LIB_FILE)

def mesh_set_lib_file(obj, filepath):
    wrapper.set_property(obj, data.PROP_MESH_LIB_FILE, filepath)

def mesh_get_tag(obj):
    return wrapper.get_property(obj, data.PROP_MESH_TAG)

def mesh_set_tag(obj, tag):
    wrapper.set_property(obj, data.PROP_MESH_TAG, tag)

# === TAGS & VERSIONS ===
def tag_parse(s):
    return [t.strip() for t in s.split(',')] if s else []

def tag_to_catalog(t):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, t))

def version_bump(v):
    return (v[0], v[1], v[2] + 1)

def version_from_string(s):
    return tuple(int(p) for p in s.split('_'))

def version_to_string(v):
    return '_'.join(map(str, v))

# === FILE PATHS ===
def file_scan_versions(mesh_name, lib_path):
    root = file_find_library_root(lib_path)
    if not root: return []
    folder = os.path.join(root, data.VERSIONS_FOLDER_NAME, mesh_name)
    if not os.path.exists(folder): return []
    
    prefix, suffix = f"{mesh_name}_", ".blend"
    versions = []
    for f in os.listdir(folder):
        if f.startswith(prefix) and f.endswith(suffix):
            try: versions.append(version_from_string(f[len(prefix):-len(suffix)]))
            except: pass
    versions.sort()
    return versions

def file_find_library_root(lib_path):
    if not lib_path: return None
    lib_path = os.path.expanduser(lib_path)
    if os.path.exists(os.path.join(lib_path, data.VERSIONS_FOLDER_NAME)): return lib_path
    try:
        for n in os.listdir(lib_path):
            sub = os.path.join(lib_path, n)
            if os.path.isdir(sub) and os.path.exists(os.path.join(sub, data.VERSIONS_FOLDER_NAME)): return sub
    except: pass
    return None

def file_ensure_versions_folder(mesh_name, lib_root):
    os.makedirs(os.path.join(lib_root, data.VERSIONS_FOLDER_NAME, mesh_name), exist_ok=True)

def file_build_version_path(mesh_name, ver_str, lib_root):
    return os.path.join(lib_root, data.VERSIONS_FOLDER_NAME, mesh_name, f"{mesh_name}_{ver_str}.blend")

def file_build_lib_path(mesh_name, lib_root):
    if not lib_root: return ""
    return os.path.join(os.path.expanduser(lib_root), f"{mesh_name}.blend")

def file_prepare_lib_path(path):
    if not path.endswith('.blend'): path += '.blend'
    folder = os.path.dirname(path)
    if folder: os.makedirs(folder, exist_ok=True)
    return path

def file_exists(path):
    return os.path.exists(path)

# === LIBRARY OPERATIONS ===
def library_write_object(obj, filepath):
    blocks = {obj, obj.data} if obj.data else {obj}
    blocks.update(wrapper.get_mesh_materials(obj))
    wrapper.write_libraries(filepath, blocks)

def library_update_from_object(obj, lib_filepath, tag):
    if not wrapper.has_asset_data(obj): wrapper.mark_asset(obj)
    if tag and wrapper.has_asset_data(obj): wrapper.set_asset_catalog(obj, tag_to_catalog(tag))
    library_write_object(obj, lib_filepath)

def library_update_from_file(source_path, lib_filepath, tag):
    existing = set(wrapper.get_all_objects().keys())
    with wrapper.load_library(source_path) as (data_from, data_to):
        data_to.objects = data_from.objects
    loaded = [ob for ob in wrapper.get_all_objects() if ob.name not in existing]
    for ob in loaded:
        if not wrapper.has_asset_data(ob): wrapper.mark_asset(ob)
        if tag and wrapper.has_asset_data(ob): wrapper.set_asset_catalog(ob, tag_to_catalog(tag))
        library_write_object(ob, lib_filepath)
        wrapper.remove_object(ob)