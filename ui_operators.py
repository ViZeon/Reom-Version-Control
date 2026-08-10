"""UI logic (draw, invoke, execute) lives here."""

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
        self.layout.prop(wrapper.get_prefs(), data.PREF_PROP_LIB_PATH)
    def execute(self, context):
        return {'FINISHED'}

class REOM_VC_OT_setup_lib_file(bpy.types.Operator):
    bl_idname = data.OP_SETUP_LIB_FILE_ID
    bl_label = data.OP_SETUP_LIB_FILE_LABEL
    filepath: bpy.props.StringProperty(name="Library File", subtype='FILE_PATH')

    def invoke(self, context, event):
        obj = wrapper.get_active_object()
        if not obj: return self._cancel(data.ERROR_NO_OBJECT)
        if not self.filepath:
            self.filepath = functions.file_build_lib_path(functions.mesh_get_name(obj), wrapper.get_prefs().lib_path)
        return context.window_manager.invoke_props_dialog(self, width=400)

    def draw(self, context):
        self.layout.label(text=data.OP_SETUP_LIB_FILE_TEXT)
        self.layout.prop(self, "filepath")

    def execute(self, context):
        path = functions.file_prepare_lib_path(wrapper.abspath(self.filepath))
        if not functions.file_exists(path): wrapper.save_as_mainfile(path)
        functions.mesh_set_lib_file(wrapper.get_active_object(), path)
        self.report({'INFO'}, f"Library file set: {path}")
        return {'FINISHED'}

    def _cancel(self, msg):
        self.report({'ERROR'}, msg)
        return {'CANCELLED'}

class REOM_VC_OT_save(bpy.types.Operator):
    bl_idname = data.OP_SAVE_ID
    bl_label = data.OP_SAVE_LABEL
    def execute(self, context):
        obj = wrapper.get_active_object()
        if not obj: return self._cancel(data.ERROR_NO_OBJECT)
        
        lib_file = functions.mesh_get_lib_file(obj)
        if not lib_file:
            wrapper.invoke_operator(data.OP_SETUP_LIB_FILE_ID)
            return {'CANCELLED'}
        
        mesh_name = functions.mesh_get_name(obj)
        root = wrapper.get_prefs().lib_path
        current_ver = functions.mesh_get_version(obj)
        new_ver = functions.version_bump(current_ver) if current_ver else (1, 0, 0)
        ver_str = functions.version_to_string(new_ver)
        
        functions.file_ensure_versions_folder(mesh_name, root)
        functions.library_write_object(obj, functions.file_build_version_path(mesh_name, ver_str, root))
        functions.library_update_from_object(obj, lib_file, functions.mesh_get_tag(obj))
        functions.mesh_set_version(obj, new_ver)
        
        self.report({'INFO'}, f"Saved {mesh_name} {ver_str}")
        return {'FINISHED'}

    def _cancel(self, msg):
        self.report({'ERROR'}, msg)
        return {'CANCELLED'}

class REOM_VC_OT_highlight(bpy.types.Operator):
    bl_idname = data.OP_HIGHLIGHT_ID
    bl_label = data.OP_HIGHLIGHT_LABEL
    version_str: bpy.props.StringProperty()

    def invoke(self, context, event):
        if self.version_str: return self.execute(context)
        obj = wrapper.get_active_object()
        if not obj: return self._cancel(data.ERROR_NO_OBJECT)
        if not functions.file_scan_versions(functions.mesh_get_name(obj), wrapper.get_prefs().lib_path):
            return self._cancel("No versions found")
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        vers = functions.file_scan_versions(functions.mesh_get_name(obj), wrapper.get_prefs().lib_path)
        self.layout.label(text="Pick version to highlight:")
        for v in vers:
            op = self.layout.operator(data.OP_HIGHLIGHT_ID, text=functions.version_to_string(v))
            op.version_str = functions.version_to_string(v)

    def execute(self, context):
        obj = wrapper.get_active_object()
        lib_file = functions.mesh_get_lib_file(obj)
        if not lib_file: return self._cancel(data.ERROR_NO_LIB_FILE)
        
        ver_path = functions.file_build_version_path(functions.mesh_get_name(obj), self.version_str, wrapper.get_prefs().lib_path)
        functions.library_update_from_file(ver_path, lib_file, functions.mesh_get_tag(obj))
        self.report({'INFO'}, f"Highlighted {functions.mesh_get_name(obj)} {self.version_str}")
        return {'FINISHED'}

    def _cancel(self, msg):
        self.report({'ERROR'}, msg)
        return {'CANCELLED'}

class REOM_VC_OT_set_tag(bpy.types.Operator):
    bl_idname = data.OP_SET_TAG_ID
    bl_label = data.OP_SET_TAG_LABEL
    tag: bpy.props.StringProperty()

    def invoke(self, context, event):
        if self.tag: return self.execute(context)
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        tags = functions.tag_parse(wrapper.get_prefs().tags)
        self.layout.prop(self, "tag")
        if tags:
            self.layout.label(text="Existing tags:")
            for t in tags:
                op = self.layout.operator(data.OP_SET_TAG_ID, text=t)
                op.tag = t

    def execute(self, context):
        obj = wrapper.get_active_object()
        if not obj: return self._cancel(data.ERROR_NO_OBJECT)
        functions.mesh_set_tag(obj, self.tag)
        self.report({'INFO'}, f"Tag set: {self.tag}")
        return {'FINISHED'}

    def _cancel(self, msg):
        self.report({'ERROR'}, msg)
        return {'CANCELLED'}

class REOM_VC_OT_test_scan(bpy.types.Operator):
    bl_idname = data.OP_TEST_SCAN_ID
    bl_label = data.OP_TEST_SCAN_LABEL
    def execute(self, context):
        obj = wrapper.get_active_object()
        if not obj:
            print("No active object selected")
            return {'CANCELLED'}
        
        mesh_name = functions.mesh_get_name(obj)
        lib_path = wrapper.get_prefs().lib_path
        if not lib_path:
            print("No library path set in preferences")
            return {'CANCELLED'}
        
        vers = functions.file_scan_versions(mesh_name, lib_path)
        if vers:
            print(f"Mesh '{mesh_name}' has versions: {', '.join(functions.version_to_string(v) for v in vers)}")
        else:
            print(f"Mesh '{mesh_name}' has no versions in library")
        return {'FINISHED'}