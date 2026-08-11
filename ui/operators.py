"""UI logic for Operators."""
import bpy
from .. import wrapper, functions, data
from ..utils.tests import run_tests

def _report(op, msg, type=data.REPORT_ERROR):
    op.report({type}, msg)
    return {data.OP_CANCEL} if type == data.REPORT_ERROR else {data.OP_FINISH}

def _get_cats(self, context):
    obj = wrapper.get_active_obj()
    if not obj: return []
    lib = functions.get_lib(obj)
    if not lib: return []
    cats = functions.read_cats(lib)
    return [(cid, name, name) for name, cid in cats.items()]

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
    
    asset_name: bpy.props.StringProperty(name=data.TEXT_ASSET_NAME)
    filepath: bpy.props.StringProperty(name=data.TEXT_FILEPATH_LABEL, subtype=data.SUBTYPE_FILE, description=data.TEXT_FILEPATH_DESC)
    
    @classmethod
    def poll(cls, ctx): return wrapper.get_active_obj() is not None
    
    def invoke(self, ctx, ev):
        obj = wrapper.get_active_obj()
        if not self.asset_name: self.asset_name = functions.get_name(obj)
        if not self.filepath: self.filepath = functions.get_default_lib_path(obj)
        return ctx.window_manager.invoke_props_dialog(self, width=data.WIDTH_LARGE)
        
    def draw(self, ctx):
        self.layout.label(text=data.TEXT_SELECT_LIB)
        self.layout.prop(self, data.PROP_ASSET_NAME)
        self.layout.prop(self, data.PROP_FILEPATH)
        
    def execute(self, ctx):
        return _report(self, functions.setup_lib(wrapper.get_active_obj(), self.asset_name, self.filepath), data.REPORT_INFO)

class REOM_VC_OT_setup_cat(bpy.types.Operator):
    bl_idname = data.OP_SETUP_CAT
    bl_label = data.OP_SETUP_CAT_LABEL
    
    existing: bpy.props.EnumProperty(items=_get_cats, name=data.TEXT_EXISTING)
    new_cat: bpy.props.StringProperty(name=data.TEXT_NEW_CAT)
    
    @classmethod
    def poll(cls, ctx): return wrapper.get_active_obj() is not None
    
    def invoke(self, ctx, ev): return ctx.window_manager.invoke_props_dialog(self, width=data.WIDTH_SMALL)
        
    def draw(self, ctx):
        self.layout.label(text=data.TEXT_SELECT_CAT)
        self.layout.prop(self, data.PROP_EXISTING)
        self.layout.prop(self, data.PROP_NEW_CAT)
        
    def execute(self, ctx):
        obj = wrapper.get_active_obj()
        if self.new_cat: cid = functions.add_cat(functions.get_lib(obj), self.new_cat)
        elif self.existing: cid = self.existing
        else: return _report(self, data.ERR_NO_CAT)
        
        functions.assign_cat(obj, cid)
        return _report(self, functions.save_version(obj), data.REPORT_INFO)

class REOM_VC_OT_version(bpy.types.Operator):
    bl_idname = data.OP_VERSION
    bl_label = data.OP_VERSION_LABEL
    action: bpy.props.EnumProperty(items=data.ITEM_ACTIONS, default=data.ACT_SAVE)
    
    @classmethod
    def poll(cls, ctx): return wrapper.get_active_obj() is not None
    
    def execute(self, ctx):
        obj = wrapper.get_active_obj()
        if functions.is_linked(obj): return _report(self, "Object is linked. Enter Edit mode first.")
        if not functions.get_lib(obj): wrapper.invoke(data.OP_SETUP); return {data.OP_CANCEL}
        if not functions.get_cat(obj): wrapper.invoke(data.OP_SETUP_CAT); return {data.OP_CANCEL}
        return _report(self, functions.save_version(obj, self.action), data.REPORT_INFO)

class REOM_VC_OT_set_main(bpy.types.Operator):
    bl_idname = data.OP_SET_MAIN
    bl_label = data.TEXT_SET_MAIN
    version_str: bpy.props.StringProperty()
    
    @classmethod
    def poll(cls, ctx): return wrapper.get_active_obj() is not None
    
    def execute(self, ctx):
        obj = wrapper.get_active_obj()
        if not functions.get_lib(obj): return _report(self, data.ERR_NO_LIB)
        return _report(self, functions.set_main_version(obj, self.version_str), data.REPORT_INFO)

class REOM_VC_OT_enter_edit(bpy.types.Operator):
    bl_idname = data.OP_ENTER_EDIT
    bl_label = data.OP_ENTER_EDIT_LABEL
    @classmethod
    def poll(cls, ctx): return wrapper.get_active_obj() is not None
    def execute(self, ctx): return _report(self, functions.enter_edit(wrapper.get_active_obj()), data.REPORT_INFO)

class REOM_VC_OT_end_edit(bpy.types.Operator):
    bl_idname = data.OP_END_EDIT
    bl_label = data.OP_END_EDIT_LABEL
    @classmethod
    def poll(cls, ctx): return wrapper.get_active_obj() is not None
    def execute(self, ctx): return _report(self, functions.end_edit(wrapper.get_active_obj()), data.REPORT_INFO)

class REOM_VC_OT_test(bpy.types.Operator):
    bl_idname = data.OP_TEST
    bl_label = data.OP_TEST_LABEL
    @classmethod
    def poll(cls, ctx): return wrapper.get_active_obj() is not None
    def execute(self, ctx):
        print(functions.scan_info(wrapper.get_active_obj()))
        return {data.OP_FINISH}

class REOM_VC_OT_run_tests(bpy.types.Operator):
    bl_idname = data.OP_RUN_TESTS
    bl_label = data.OP_RUN_TESTS_LABEL
    def execute(self, ctx):
        result = run_tests()
        msg = f"Ran {result.testsRun} tests. Success: {result.wasSuccessful()}"
        print(msg)
        return _report(self, msg, data.REPORT_INFO)
