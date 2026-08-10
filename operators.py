"""All operator classes. UI logic (draw, invoke, execute) lives here."""

import os
import bpy
import uuid
from . import blender_api, funcs
from .variables_ui import (
    STARTUP_BL_IDNAME, STARTUP_LABEL, STARTUP_TEXT,
    SAVE_BL_IDNAME, SAVE_LABEL,
    SETUP_LIB_FILE_BL_IDNAME, SETUP_LIB_FILE_LABEL, SETUP_LIB_FILE_TEXT,
    HIGHLIGHT_BL_IDNAME, HIGHLIGHT_LABEL,
    SET_TAG_BL_IDNAME, SET_TAG_LABEL,
    NO_OBJECT_TEXT, NO_LIB_FILE_TEXT,
)

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
        
        mesh_name = funcs.mesh_get_name(obj)
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
            blender_api.file_save_as(path)
        
        funcs.mesh_set_lib_file(obj, path)
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
        
        lib_file = funcs.mesh_get_lib_file(obj)
        if not lib_file:
            blender_api.operator_invoke(SETUP_LIB_FILE_BL_IDNAME)
            return {'CANCELLED'}
        
        mesh_name = funcs.mesh_get_name(obj)
        prefs = context.preferences.addons[__package__].preferences
        root = prefs.lib_path
        
        current_ver = funcs.mesh_get_version(obj)
        new_ver = funcs.version_bump_current(current_ver) if current_ver else (1, 0, 0)
        ver_str = funcs.version_to_string(new_ver)
        
        ver_path = funcs.file_build_version_path(mesh_name, ver_str, root)
        funcs.file_ensure_versions_folder(mesh_name, root)
        funcs.library_write_object(obj, ver_path)
        
        tag = funcs.mesh_get_tag(obj)
        funcs.library_update_from_object(obj, lib_file, tag)
        
        funcs.mesh_set_version(obj, new_ver)
        self.report({'INFO'}, f"Saved {mesh_name} {ver_str}")
        return {'FINISHED'}

class REOM_VC_OT_highlight(bpy.types.Operator):
    bl_idname = HIGHLIGHT_BL_IDNAME
    bl_label = HIGHLIGHT_LABEL
    
    version_str: bpy.props.StringProperty()
    
    def invoke(self, context, event):
        if self.version_str:
            return self.execute(context)
        
        obj = blender_api.context_get_active_object()
        if not obj:
            self.report({'ERROR'}, NO_OBJECT_TEXT)
            return {'CANCELLED'}
        
        mesh_name = funcs.mesh_get_name(obj)
        prefs = context.preferences.addons[__package__].preferences
        versions = funcs.file_scan_versions(mesh_name, prefs.lib_path)
        versions.sort()
        
        if not versions:
            self.report({'INFO'}, "No versions found")
            return {'CANCELLED'}
        
        return context.window_manager.invoke_props_dialog(self, width=300)
    
    def draw(self, context):
        obj = blender_api.context_get_active_object()
        mesh_name = funcs.mesh_get_name(obj)
        prefs = context.preferences.addons[__package__].preferences
        versions = funcs.file_scan_versions(mesh_name, prefs.lib_path)
        versions.sort()
        
        self.layout.label(text="Pick version to highlight:")
        for ver in versions:
            ver_str = funcs.version_to_string(ver)
            op = self.layout.operator(HIGHLIGHT_BL_IDNAME, text=ver_str)
            op.version_str = ver_str
    
    def execute(self, context):
        obj = blender_api.context_get_active_object()
        mesh_name = funcs.mesh_get_name(obj)
        prefs = context.preferences.addons[__package__].preferences
        root = prefs.lib_path
        lib_file = funcs.mesh_get_lib_file(obj)
        
        if not lib_file:
            self.report({'ERROR'}, NO_LIB_FILE_TEXT)
            return {'CANCELLED'}
        
        ver_path = funcs.file_build_version_path(mesh_name, self.version_str, root)
        tag = funcs.mesh_get_tag(obj)
        
        funcs.library_update_from_file(ver_path, lib_file, tag)
        self.report({'INFO'}, f"Highlighted {mesh_name} {self.version_str}")
        return {'FINISHED'}

class REOM_VC_OT_set_tag(bpy.types.Operator):
    bl_idname = SET_TAG_BL_IDNAME
    bl_label = SET_TAG_LABEL
    
    tag: bpy.props.StringProperty()
    
    def invoke(self, context, event):
        if self.tag:
            return self.execute(context)
        return context.window_manager.invoke_props_dialog(self, width=300)
    
    def draw(self, context):
        prefs = context.preferences.addons[__package__].preferences
        tags = funcs.tag_list_parse(prefs.tags)
        self.layout.prop(self, "tag")
        if tags:
            self.layout.label(text="Existing tags:")
            for t in tags:
                op = self.layout.operator(SET_TAG_BL_IDNAME, text=t)
                op.tag = t
    
    def execute(self, context):
        obj = blender_api.context_get_active_object()
        if not obj:
            self.report({'ERROR'}, NO_OBJECT_TEXT)
            return {'CANCELLED'}
        
        funcs.mesh_set_tag(obj, self.tag)
        self.report({'INFO'}, f"Tag set: {self.tag}")
        return {'FINISHED'}