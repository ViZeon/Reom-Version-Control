"""All operator classes. UI logic (draw, invoke, execute) lives here."""

import bpy
from . import wrapper, functions
from . import data

class REOM_VC_OT_startup(bpy.types.Operator):
    bl_idname = data.OP_STARTUP_ID
    bl_label = data.OP_STARTUP_LABEL
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)
    
    def draw(self, context):
        self.layout.label(text=data.OP_STARTUP_TEXT)
        prefs = context.preferences.addons[__package__].preferences
        self.layout.prop(prefs, data.PREF_PROP_LIB_PATH)
    
    def execute(self, context):
        return {'FINISHED'}

class REOM_VC_OT_setup_lib_file(bpy.types.Operator):
    bl_idname = data.OP_SETUP_LIB_FILE_ID
    bl_label = data.OP_SETUP_LIB_FILE_LABEL
    
    filepath: bpy.props.StringProperty(name="Library File", subtype='FILE_PATH')
    
    def invoke(self, context, event):
        obj = wrapper.get_active_object()
        if not obj:
            self.report({'ERROR'}, data.ERROR_NO_OBJECT)
            return {'CANCELLED'}
        
        mesh_name = functions.mesh_get_name(obj)
        prefs = context.preferences.addons[__package__].preferences
        root = prefs.lib_path
        
        if not self.filepath and root:
            self.filepath = functions.file_build_lib_path(mesh_name, root)
        
        return context.window_manager.invoke_props_dialog(self, width=400)
    
    def draw(self, context):
        self.layout.label(text=data.OP_SETUP_LIB_FILE_TEXT)
        self.layout.prop(self, "filepath")
    
    def execute(self, context):
        obj = wrapper.get_active_object()
        path = wrapper.abspath(self.filepath)
        
        path = functions.file_ensure_blend_extension(path)
        functions.file_ensure_folder_exists(path)
        
        if not functions.file_exists(path):
            wrapper.save_as_mainfile(path)
        
        functions.mesh_set_lib_file(obj, path)
        self.report({'INFO'}, f"Library file set: {path}")
        return {'FINISHED'}

class REOM_VC_OT_save(bpy.types.Operator):
    bl_idname = data.OP_SAVE_ID
    bl_label = data.OP_SAVE_LABEL
    
    def execute(self, context):
        obj = wrapper.get_active_object()
        if not obj:
            self.report({'ERROR'}, data.ERROR_NO_OBJECT)
            return {'CANCELLED'}
        
        lib_file = functions.mesh_get_lib_file(obj)
        if not lib_file:
            wrapper.invoke_operator(data.OP_SETUP_LIB_FILE_ID)
            return {'CANCELLED'}
        
        mesh_name = functions.mesh_get_name(obj)
        prefs = context.preferences.addons[__package__].preferences
        root = prefs.lib_path
        
        current_ver = functions.mesh_get_version(obj)
        new_ver = functions.version_bump_current(current_ver) if current_ver else (1, 0, 0)
        ver_str = functions.version_to_string(new_ver)
        
        ver_path = functions.file_build_version_path(mesh_name, ver_str, root)
        functions.file_ensure_versions_folder(mesh_name, root)
        functions.library_write_object(obj, ver_path)
        
        tag = functions.mesh_get_tag(obj)
        functions.library_update_from_object(obj, lib_file, tag)
        
        functions.mesh_set_version(obj, new_ver)
        self.report({'INFO'}, f"Saved {mesh_name} {ver_str}")
        return {'FINISHED'}

class REOM_VC_OT_highlight(bpy.types.Operator):
    bl_idname = data.OP_HIGHLIGHT_ID
    bl_label = data.OP_HIGHLIGHT_LABEL
    
    version_str: bpy.props.StringProperty()
    
    def invoke(self, context, event):
        if self.version_str:
            return self.execute(context)
        
        obj = wrapper.get_active_object()
        if not obj:
            self.report({'ERROR'}, data.ERROR_NO_OBJECT)
            return {'CANCELLED'}
        
        mesh_name = functions.mesh_get_name(obj)
        prefs = context.preferences.addons[__package__].preferences
        versions = functions.file_scan_versions(mesh_name, prefs.lib_path)
        
        if not versions:
            self.report({'INFO'}, "No versions found")
            return {'CANCELLED'}
        
        return context.window_manager.invoke_props_dialog(self, width=300)
    
    def draw(self, context):
        obj = wrapper.get_active_object()
        mesh_name = functions.mesh_get_name(obj)
        prefs = context.preferences.addons[__package__].preferences
        versions = functions.file_scan_versions(mesh_name, prefs.lib_path)
        
        self.layout.label(text="Pick version to highlight:")
        for ver in versions:
            ver_str = functions.version_to_string(ver)
            op = self.layout.operator(data.OP_HIGHLIGHT_ID, text=ver_str)
            op.version_str = ver_str
    
    def execute(self, context):
        obj = wrapper.get_active_object()
        mesh_name = functions.mesh_get_name(obj)
        prefs = context.preferences.addons[__package__].preferences
        root = prefs.lib_path
        lib_file = functions.mesh_get_lib_file(obj)
        
        if not lib_file:
            self.report({'ERROR'}, data.ERROR_NO_LIB_FILE)
            return {'CANCELLED'}
        
        ver_path = functions.file_build_version_path(mesh_name, self.version_str, root)
        tag = functions.mesh_get_tag(obj)
        
        functions.library_update_from_file(ver_path, lib_file, tag)
        self.report({'INFO'}, f"Highlighted {mesh_name} {self.version_str}")
        return {'FINISHED'}

class REOM_VC_OT_set_tag(bpy.types.Operator):
    bl_idname = data.OP_SET_TAG_ID
    bl_label = data.OP_SET_TAG_LABEL
    
    tag: bpy.props.StringProperty()
    
    def invoke(self, context, event):
        if self.tag:
            return self.execute(context)
        return context.window_manager.invoke_props_dialog(self, width=300)
    
    def draw(self, context):
        prefs = context.preferences.addons[__package__].preferences
        tags = functions.tag_list_parse(prefs.tags)
        self.layout.prop(self, "tag")
        if tags:
            self.layout.label(text="Existing tags:")
            for t in tags:
                op = self.layout.operator(data.OP_SET_TAG_ID, text=t)
                op.tag = t
    
    def execute(self, context):
        obj = wrapper.get_active_object()
        if not obj:
            self.report({'ERROR'}, data.ERROR_NO_OBJECT)
            return {'CANCELLED'}
        
        functions.mesh_set_tag(obj, self.tag)
        self.report({'INFO'}, f"Tag set: {self.tag}")
        return {'FINISHED'}

class REOM_VC_OT_test_scan(bpy.types.Operator):
    bl_idname = data.OP_TEST_SCAN_ID
    bl_label = data.OP_TEST_SCAN_LABEL
    
    def execute(self, context):
        obj = wrapper.get_active_object()
        if not obj:
            print("No active object selected")
            return {'CANCELLED'}
        
        mesh_name = functions.mesh_get_name(obj)
        print(f"Mesh identity: {mesh_name}")
        
        prefs = context.preferences.addons[__package__].preferences
        lib_path = prefs.lib_path
        
        if not lib_path:
            print("No library path set in preferences")
            return {'CANCELLED'}
        
        versions = functions.file_scan_versions(mesh_name, lib_path)
        
        if versions:
            ver_strings = [functions.version_to_string(v) for v in versions]
            print(f"Mesh '{mesh_name}' has versions: {', '.join(ver_strings)}")
        else:
            print(f"Mesh '{mesh_name}' has no versions in library")
        
        return {'FINISHED'}