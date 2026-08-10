"""UI logic (draw, invoke, execute) lives here."""
import bpy, os
from . import wrapper, functions, data

def _report(op, msg, type='ERROR'):
    op.report({type}, msg)
    return {'CANCELLED'}

class REOM_VC_OT_startup(bpy.types.Operator):
    bl_idname = data.OP_STARTUP
    bl_label = "Reom VC"
    def invoke(self, ctx, ev): return ctx.window_manager.invoke_props_dialog(self, width=300)
    def draw(self, ctx):
        self.layout.label(text="VC is ready.")
        self.layout.prop(wrapper.get_prefs(), "lib_path")
    def execute(self, ctx): return {'FINISHED'}

class REOM_VC_OT_setup(bpy.types.Operator):
    bl_idname = data.OP_SETUP
    bl_label = "Setup Lib File"
    filepath: bpy.props.StringProperty(subtype='FILE_PATH')
    
    def invoke(self, ctx, ev):
        obj = wrapper.get_active_obj()
        if not obj: return _report(self, data.ERR_NO_OBJ)
        if not self.filepath:
            self.filepath = functions.file_get_lib_path(functions.mesh_get_name(obj), wrapper.get_prefs().lib_path)
        return ctx.window_manager.invoke_props_dialog(self, width=400)
        
    def draw(self, ctx):
        self.layout.label(text="Select library file")
        self.layout.prop(self, "filepath")
        
    def execute(self, ctx):
        path = functions.file_prepare_path(wrapper.abspath(self.filepath))
        if not os.path.exists(path): wrapper.save_main(path)
        functions.mesh_set_lib(wrapper.get_active_obj(), path)
        return _report(self, f"Lib set: {path}", 'INFO')

class REOM_VC_OT_save(bpy.types.Operator):
    bl_idname = data.OP_SAVE
    bl_label = "Save Version"
    
    def execute(self, ctx):
        obj = wrapper.get_active_obj()
        if not obj: return _report(self, data.ERR_NO_OBJ)
        
        lib_file = functions.mesh_get_lib(obj)
        if not lib_file:
            wrapper.invoke(data.OP_SETUP)
            return {'CANCELLED'}
        
        mesh_name = functions.mesh_get_name(obj)
        root = wrapper.get_prefs().lib_path
        cur_ver = functions.mesh_get_ver(obj)
        new_ver = functions.ver_bump(cur_ver) if cur_ver else (1, 0, 0)
        v_str = functions.ver_str(new_ver)
        
        ver_path = functions.file_get_version_path(mesh_name, v_str, root)
        functions.lib_write(obj, ver_path)
        functions.lib_update(obj, lib_file, functions.mesh_get_tag(obj))
        functions.mesh_set_ver(obj, new_ver)
        return _report(self, f"Saved {mesh_name} {v_str}", 'INFO')

class REOM_VC_OT_highlight(bpy.types.Operator):
    bl_idname = data.OP_HIGHLIGHT
    bl_label = "Highlight"
    version_str: bpy.props.StringProperty()
    
    def invoke(self, ctx, ev):
        if self.version_str: return self.execute(ctx)
        obj = wrapper.get_active_obj()
        if not obj: return _report(self, data.ERR_NO_OBJ)
        if not functions.file_scan_versions(functions.mesh_get_name(obj), wrapper.get_prefs().lib_path):
            return _report(self, "No versions found")
        return ctx.window_manager.invoke_props_dialog(self, width=300)
        
    def draw(self, ctx):
        vers = functions.file_scan_versions(functions.mesh_get_name(wrapper.get_active_obj()), wrapper.get_prefs().lib_path)
        self.layout.label(text="Pick version:")
        for v in vers:
            op = self.layout.operator(data.OP_HIGHLIGHT, text=functions.ver_str(v))
            op.version_str = functions.ver_str(v)
            
    def execute(self, ctx):
        obj = wrapper.get_active_obj()
        lib_file = functions.mesh_get_lib(obj)
        if not lib_file: return _report(self, data.ERR_NO_LIB)
        
        mesh_name = functions.mesh_get_name(obj)
        ver_path = functions.file_get_version_path(mesh_name, self.version_str, wrapper.get_prefs().lib_path)
        functions.lib_promote_from_file(ver_path, lib_file, functions.mesh_get_tag(obj))
        return _report(self, f"Highlighted {mesh_name} {self.version_str}", 'INFO')

class REOM_VC_OT_tag(bpy.types.Operator):
    bl_idname = data.OP_TAG
    bl_label = "Set Tag"
    tag: bpy.props.StringProperty()
    
    def invoke(self, ctx, ev):
        return self.execute(ctx) if self.tag else ctx.window_manager.invoke_props_dialog(self, width=300)
        
    def draw(self, ctx):
        tags = functions.tag_parse(wrapper.get_prefs().tags)
        self.layout.prop(self, "tag")
        if tags:
            self.layout.label(text="Existing:")
            for t in tags:
                op = self.layout.operator(data.OP_TAG, text=t)
                op.tag = t
                
    def execute(self, ctx):
        obj = wrapper.get_active_obj()
        if not obj: return _report(self, data.ERR_NO_OBJ)
        functions.mesh_set_tag(obj, self.tag)
        return _report(self, f"Tag set: {self.tag}", 'INFO')

class REOM_VC_OT_test(bpy.types.Operator):
    bl_idname = data.OP_TEST
    bl_label = "Test Scan"
    def execute(self, ctx):
        obj = wrapper.get_active_obj()
        if not obj: print("No obj"); return {'CANCELLED'}
        
        mesh_name = functions.mesh_get_name(obj)
        lib_path = wrapper.get_prefs().lib_path
        if not lib_path: print("No lib path"); return {'CANCELLED'}
        
        vers = functions.file_scan_versions(mesh_name, lib_path)
        if vers: print(f"Mesh '{mesh_name}' versions: {', '.join(functions.ver_str(v) for v in vers)}")
        else: print(f"Mesh '{mesh_name}' has no versions")
        return {'FINISHED'}