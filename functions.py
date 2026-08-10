"""Pure functions and business logic. No operator classes. No bpy calls."""

import os
import sys
import uuid
from . import wrapper
from . import data

# === ADDON LIFECYCLE ===

def addon_register(class_list):
    wrapper.register_classes(class_list)
    
    mod = sys.modules.get(__package__)
    auto_enabled = mod and getattr(mod, data.AUTO_ENABLE_FLAG, False)
    
    if auto_enabled:
        setattr(mod, data.AUTO_ENABLE_FLAG, False)
    else:
        def _startup():
            window = wrapper.get_windows()[0] if wrapper.get_windows() else None
            area = None
            if window:
                for a in window.screen.areas:
                    if a.type == 'VIEW_3D':
                        area = a
                        break
            
            if window and area:
                with wrapper.temp_override(window, area):
                    wrapper.invoke_operator(data.OP_STARTUP_ID)
            return None
            
        wrapper.register_timer(_startup, data.FIRST_RUN_DELAY)

def addon_unregister(class_list):
    wrapper.unregister_classes(class_list)

# === MESH IDENTITY ===

def mesh_get_name(obj):
    name = wrapper.get_property(obj, data.PROP_MESH_NAME)
    if name is None:
        name = obj.name
    return name

def mesh_set_name(obj, name):
    wrapper.set_property(obj, data.PROP_MESH_NAME, name)

def mesh_get_version(obj):
    ver_str = wrapper.get_property(obj, data.PROP_MESH_VERSION)
    if ver_str:
        return version_from_string(ver_str)
    return None

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

# === TAG SYSTEM ===

def tag_list_parse(tags_string):
    if not tags_string:
        return []
    return [t.strip() for t in tags_string.split(',') if t.strip()]

def tag_list_join(tags_list):
    return ', '.join(tags_list)

def tag_to_catalog(tag):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, tag))

# === VERSION MATH ===

def version_bump_current(v):
    return (v[0], v[1], v[2] + 1)

def version_from_string(s):
    parts = s.split('_')
    return tuple(int(p) for p in parts)

def version_to_string(v):
    return '_'.join(str(n) for n in v)

# === FILE PATHS ===

def file_scan_versions(mesh_name, lib_path):
    versions = []
    lib_path = file_find_library_root(lib_path)
    if not lib_path:
        return versions
    
    versions_folder = os.path.join(lib_path, data.VERSIONS_FOLDER_NAME, mesh_name)
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
    
    versions.sort()
    return versions

def file_find_library_root(lib_path):
    if not lib_path:
        return None
    
    lib_path = os.path.expanduser(lib_path)
    
    if os.path.exists(os.path.join(lib_path, data.VERSIONS_FOLDER_NAME)):
        return lib_path
    
    try:
        for name in os.listdir(lib_path):
            sub = os.path.join(lib_path, name)
            if os.path.isdir(sub) and os.path.exists(os.path.join(sub, data.VERSIONS_FOLDER_NAME)):
                return sub
    except:
        pass
    
    return None

def file_ensure_versions_folder(mesh_name, lib_root):
    folder = os.path.join(lib_root, data.VERSIONS_FOLDER_NAME, mesh_name)
    os.makedirs(folder, exist_ok=True)

def file_build_version_path(mesh_name, ver_str, lib_root):
    folder = os.path.join(lib_root, data.VERSIONS_FOLDER_NAME, mesh_name)
    filename = f"{mesh_name}_{ver_str}.blend"
    return os.path.join(folder, filename)

def file_build_lib_path(mesh_name, lib_root):
    if not lib_root:
        return ""
    root = os.path.expanduser(lib_root)
    return os.path.join(root, f"{mesh_name}.blend")

def file_exists(path):
    return os.path.exists(path)

def file_ensure_blend_extension(path):
    if not path.endswith('.blend'):
        path += '.blend'
    return path

def file_ensure_folder_exists(path):
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)

# === LIBRARY FILE OPERATIONS ===

def library_write_object(obj, filepath):
    """Save object and its data blocks to a .blend file. Plain file, no asset setup."""
    blocks = {obj}
    if obj.data:
        blocks.add(obj.data)
    for mat in obj.data.materials:
        if mat:
            blocks.add(mat)
    wrapper.write_libraries(filepath, blocks, fake_user=True)

def library_update_from_object(obj, lib_filepath, tag):
    """Mark asset on original object, write clean file. No load/writeback."""
    if not obj.asset_data:
        wrapper.mark_asset(obj)
    if tag and obj.asset_data:
        wrapper.set_asset_catalog(obj, tag_to_catalog(tag))
    library_write_object(obj, lib_filepath)

def library_update_from_file(source_path, lib_filepath, tag):
    """Load backup, mark asset, write ONE object to library, cleanup."""
    existing = set(wrapper.get_all_objects().keys())
    
    with wrapper.load_library(source_path, link=False) as (data_from, data_to):
        data_to.objects = data_from.objects
    
    loaded = [ob for ob in wrapper.get_all_objects() if ob.name not in existing]
    
    for ob in loaded:
        if not ob.asset_data:
            wrapper.mark_asset(ob)
        if tag and ob.asset_data:
            wrapper.set_asset_catalog(ob, tag_to_catalog(tag))
        library_write_object(ob, lib_filepath)
        wrapper.remove_object(ob)