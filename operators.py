import bpy
from .variables import DIALOG_WIDTH
from .variables_ui import STARTUP_BL_IDNAME, STARTUP_LABEL, STARTUP_TEXT, PROP_NAME_LIB_PATH

class REOM_VC_OT_startup(bpy.types.Operator):
    bl_idname = STARTUP_BL_IDNAME
    bl_label = STARTUP_LABEL
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=DIALOG_WIDTH)
    
    def draw(self, context):
        self.layout.label(text=STARTUP_TEXT)
        prefs = context.preferences.addons[__package__].preferences
        self.layout.prop(prefs, "lib_path")
    
    def execute(self, context):
        return {'FINISHED'}