"""UI logic for Operators."""
import bpy, os
from . import wrapper, functions, data

def _report(op, msg, type=data.REPORT_ERROR):
    op.report({type}, msg)
    return {data.OP_CANCEL}

class REOM_VC_OT_startup(bpy.types.Operator):
    bl_idname = data.OP_STARTUP
    bl_label = data.PANEL_LABEL
    def invoke(self, ctx, ev): return ctx.window_manager.invoke_props_dialog(self, width=data.WIDTH_SMALL)
    def draw(self, ctx):
        self.layout.label(text=data.TEXT_READY)
        self.layout.prop(wrapper.get_prefs(), data.PREF_LIB)
    def execute(self, ctx): return {data.OP_FINISH}

class REOM_VC_OT_setup(bpy.types.Operator):
    bl_idname = data.OP_SETUP
    bl_label = data.OP_SETUP_LABEL
    filepath: bpy.props.StringProperty(subtype=data.SUBTYPE_FILE)
    
    def invoke(self, ctx, ev):
        obj = wrapper.get_active_obj()
        if not obj: return _report(self, data.ERR_NO_OBJ)
        if not self.filepath:
            root = wrapper.get_prefs().lib_path
            self.filepath = os.path.join(os.path.expanduser(root), f"{functions.get_name(obj)}{data.BLEND_EXT}") if root else ""
        return ctx.window_manager.invoke_props_dialog(self, width=data.WIDTH_LARGE)
        
    def draw(self, ctx):
        self.layout.label(text=data.TEXT_SELECT_LIB)
        self.layout.prop(self, data.PROP_FILEPATH)
        
    def execute(self, ctx):
        obj = wrapper.get_active_obj()
        if not obj: return _report(self, data.ERR_NO_OBJ)
        return _report(self, functions.setup_lib(obj, self.filepath), data.REPORT_INFO)

class REOM_VC_OT_save(bpy.types.Operator):
    bl_idname = data.OP_SAVE
    bl_label = data.OP_SAVE_LABEL
    
    def execute(self, ctx):
        obj = wrapper.get_active_obj()
        if not obj: return _report(self, data.ERR_NO_OBJ)
        if not functions.get_lib(obj):
            wrapper.invoke(data.OP_SETUP)
            return {data.OP_CANCEL}
        return _report(self, functions.save_version(obj), data.REPORT_INFO)

class REOM_VC_OT_highlight(bpy.types.Operator):
    bl_idname = data.OP_HIGHLIGHT
    bl_label = data.TEXT_HIGHLIGHT
    version_str: bpy.props.StringProperty()
    
    def invoke(self, ctx, ev):
        if self.version_str: return self.execute(ctx)
        obj = wrapper.get_active_obj()
        if not obj: return _report(self, data.ERR_NO_OBJ)
        if not functions.scan_versions(functions.get_name(obj), wrapper.get_prefs().lib_path):
            return _report(self, data.TEXT_NO_VER)
        return ctx.window_manager.invoke_props_dialog(self, width=data.WIDTH_SMALL)
        
    def draw(self, ctx):
        vers = functions.scan_versions(functions.get_name(wrapper.get_active_obj()), wrapper.get_prefs().lib_path)
        self.layout.label(text=data.TEXT_PICK_VER)
        for v in vers:
            op = self.layout.operator(data.OP_HIGHLIGHT, text=functions.str_ver(v))
            op.version_str = functions.str_ver(v)
            
    def execute(self, ctx):
        obj = wrapper.get_active_obj()
        if not obj: return _report(self, data.ERR_NO_OBJ)
        if not functions.get_lib(obj): return _report(self, data.ERR_NO_LIB)
        return _report(self, functions.highlight_version(obj, self.version_str), data.REPORT_INFO)

class REOM_VC_OT_tag(bpy.types.Operator):
    bl_idname = data.OP_TAG
    bl_label = data.OP_TAG_LABEL
    tag: bpy.props.StringProperty()
    
    def invoke(self, ctx, ev):
        return self.execute(ctx) if self.tag else ctx.window_manager.invoke_props_dialog(self, width=data.WIDTH_SMALL)
        
    def draw(self, ctx):
        tags = functions.parse_tags(wrapper.get_prefs().tags)
        self.layout.prop(self, data.PROP_TAG_UI)
        if tags:
            self.layout.label(text=data.TEXT_EXISTING)
            for t in tags:
                op = self.layout.operator(data.OP_TAG, text=t)
                op.tag = t
                
    def execute(self, ctx):
        obj = wrapper.get_active_obj()
        if not obj: return _report(self, data.ERR_NO_OBJ)
        return _report(self, functions.assign_tag(obj, self.tag), data.REPORT_INFO)

class REOM_VC_OT_test(bpy.types.Operator):
    bl_idname = data.OP_TEST
    bl_label = data.OP_TEST_LABEL
    def execute(self, ctx):
        obj = wrapper.get_active_obj()
        if not obj: return _report(self, data.ERR_NO_OBJ)
        print(functions.scan_info(obj))
        return {data.OP_FINISH}