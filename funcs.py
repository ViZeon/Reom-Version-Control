"""Operator classes + all business logic. Organized by prefix regions."""

import os
import sys
import shutil
import bpy
from . import blender_api
from .variables import (
    FIRST_RUN_DELAY, VERSIONS_FOLDER_NAME,
    MESH_PROP_NAME, MESH_PROP_VERSION, MESH_PROP_LIB_FILE, MESH_PROP_TAG,
    DEFAULT_TAGS,
)
from .variables_ui import (
    STARTUP_BL_IDNAME, STARTUP_LABEL, STARTUP_TEXT,
    SAVE_BL_IDNAME, SAVE_LABEL,
    SETUP_LIB_FILE_BL_IDNAME, SETUP_LIB_FILE_LABEL, SETUP_LIB_FILE_TEXT,
    HIGHLIGHT_BL_IDNAME, HIGHLIGHT_LABEL,
    SET_TAG_BL_IDNAME, SET_TAG_LABEL,
    NO_OBJECT_TEXT, NO_LIB_FILE_TEXT,
)

# Module cache for highlight dialog
_highlight_versions_cache = []

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

class REOM_VC_OT_setup_lib_file(bpy.types.Operator):
    bl_idname = SETUP_LIB_FILE_BL_IDNAME
    bl_label = SETUP_LIB_FILE_LABEL
    
    filepath: bpy.props.StringProperty(name="Library File", subtype='FILE_PATH')
    
    def invoke(self, context, event):
        obj = blender_api.context_get_active_object()
        if not obj:
            self.report({'ERROR'}, NO_OBJECT_TEXT)
            return {'CANCELLED'}
        
        mesh_name = mesh_get_name(obj)
        prefs = context.preferences.addons[__package__].preferences
        root = prefs.lib_path
        
        if not self.filepath and root:
            default = os.path.join(os.path.expanduser(root), f"{mesh_name}.blend")
            self.filepath = default
        
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context):
        self.layout.label(text=SETUP_LIB_FILE_TEXT)
        self.layout.prop(self, "filepath")
    
    def execute(self, context):
        obj = blender_api.context_get_active_object()
        path = blender_api.path_abspath(self.filepath)
        
        if not path.endswith('.blend'):
            path += '.blend'
        
        folder = os.path.dirname(path)
        os.makedirs(folder, exist_ok=True)
        
        if not os.path.exists(path):
            bpy.ops.wm.save_as_mainfile(filepath=path, copy=True)
        
        mesh_set_lib_file(obj, path)
        self.report({'INFO'}, f"Library file set: {path}")
        return {'FINISHED'}

class REOM_VC_OT_save(bpy.types.Operator):
    bl_idname = SAVE_BL_IDNAME
    bl_label = SAVE_LABEL
    
    def execute(self, context):
        obj = blender_api.context_get_active_object()
        if not obj:
            self.report({'ERROR'}, NO_OBJECT_TEXT)
            return {'CANCELLED'}
        
        lib_file = mesh_get_lib_file(obj)
        if not lib_file:
            blender_api.operator_invoke(SETUP_LIB_FILE_BL_IDNAME)
            return {'CANCELLED'}
        
        mesh_name = mesh_get_name(obj)
        prefs = context.preferences.addons[__package__].preferences
        root = prefs.lib_path
        
        current_ver = mesh_get_version(obj)
        new_ver = version_bump_current(current_ver) if current_ver else (1, 0, 0)
        ver_str = version_to_string(new_ver)
        
        # Write version backup
        ver_path = file_build_version_path(mesh_name, ver_str, root)
        file_ensure_versions_folder(mesh_name, root)
        _write_object_to_blend(obj, ver_path)
        
        # Update library file
        tag = mesh_get_tag(obj)
        _copy_to_library_file(obj, lib_file, tag)
        
        mesh_set_version(obj, new_ver)
        self.report({'INFO'}, f"Saved {mesh_name} {ver_str}")
        return {'FINISHED'}

class REOM_VC_OT_highlight(bpy.types.Operator):
    bl_idname = HIGHLIGHT_BL_IDNAME
    bl_label = HIGHLIGHT_LABEL
    
    version_index: bpy.props.IntProperty(default=-1)
    
    def invoke(self, context, event):
        obj = blender_api.context_get_active_object()
        if not obj:
            self.report({'ERROR'}, NO_OBJECT_TEXT)
            return {'CANCELLED'}
        
        mesh_name = mesh_get_name(obj)
        prefs = context.preferences.addons[__package__].preferences
        versions = file_scan_versions(mesh_name, prefs.lib_path)
        versions.sort()
        
        global _highlight_versions_cache
        _highlight_versions_cache = versions
        
        return context.window_manager.invoke_props_dialog(self, width=300)
    
    def draw(self, context):
        self.layout.label(text="Pick version to highlight:")
        for i, ver in enumerate(_highlight_versions_cache):
            ver_str = version_to_string(ver)
            self.layout.prop(self, "version_index", text=ver_str, index=i)
    
    def execute(self, context):
        if self.version_index < 0 or self.version_index >= len(_highlight_versions_cache):
            self.report({'ERROR'}, "No version selected")
            return {'CANCELLED'}
        
        obj = blender_api.context_get_active_object()
        mesh_name = mesh_get_name(obj)
        ver = _highlight_versions_cache[self.version_index]
        ver_str = version_to_string(ver)
        
        prefs = context.preferences.addons[__package__].preferences
        root = prefs.lib_path
        lib_file = mesh_get_lib_file(obj)
        
        ver_path = file_build_version_path(mesh_name, ver_str, root)
        tag = mesh_get_tag(obj)
        
        _copy_file_to_library(ver_path, lib_file, tag)
        self.report({'INFO'}, f"Highlighted {mesh_name} {ver_str}")
        return {'FINISHED'}

class REOM_VC_OT_set_tag(bpy.types.Operator):
    bl_idname = SET_TAG_BL_IDNAME
    bl_label = SET_TAG_LABEL
    
    tag: bpy.props.StringProperty(name="Tag")
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)
    
    def draw(self, context):
        prefs = context.preferences.addons[__package__].preferences
        tags = tag_list_parse(prefs.tags)
        self.layout.prop(self, "tag")
        if tags:
            self.layout.label(text="Existing tags:")
            for t in tags:
                row = self.layout.row()
                row.label(text=t)
                op = row.operator(SET_TAG_BL_IDNAME, text="Pick")
                op.tag = t
    
    def execute(self, context):
        obj = blender_api.context_get_active_object()
        if not obj:
            self.report({'ERROR'}, NO_OBJECT_TEXT)
            return {'CANCELLED'}
        
        mesh_set_tag(obj, self.tag)
        self.report({'INFO'}, f"Tag set: {self.tag}")
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

def _write_object_to_blend(obj, filepath):
    """Save only this object and its data to a new .blend file."""
    blocks = {obj}
    if obj.data:
        blocks.add(obj.data)
    for mat in obj.data.materials:
        if mat:
            blocks.add(mat)
    bpy.data.libraries.write(filepath, blocks, fake_user=True)

def _copy_to_library_file(obj, lib_filepath, tag):
    """Save object into the library file and mark as asset."""
    if not obj.asset_data:
        blender_api.asset_mark(obj)
    if tag and obj.asset_data:
        catalog = _tag_to_catalog(tag)
        blender_api.asset_set_catalog(obj, catalog)
    
    blocks = {obj}
    if obj.data:
        blocks.add(obj.data)
    for mat in obj.data.materials:
        if mat:
            blocks.add(mat)
    
    bpy.data.libraries.write(lib_filepath, blocks, fake_user=True)

def _copy_file_to_library(source_path, lib_filepath, tag):
    """Copy a version file into the library file and mark as asset."""
    shutil.copy2(source_path, lib_filepath)
    
    with bpy.data.libraries.load(lib_filepath, link=False) as (data_from, data_to):
        data_to.objects = data_from.objects
    
    blocks = set()
    for ob in data_to.objects:
        if not ob.asset_data:
            blender_api.asset_mark(ob)
        if tag and ob.asset_data:
            catalog = _tag_to_catalog(tag)
            blender_api.asset_set_catalog(ob, catalog)
        blocks.add(ob)
        if ob.data:
            blocks.add(ob.data)
        for mat in ob.data.materials:
            if mat:
                blocks.add(mat)
    
    if blocks:
        bpy.data.libraries.write(lib_filepath, blocks, fake_user=True)

def _tag_to_catalog(tag):
    """Convert tag string to catalog ID. Creates if needed."""
    # For now, simple hash. Future: read/write blender_assets.cats.txt
    return str(hash(tag) % (2**31))