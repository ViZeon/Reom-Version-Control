import bpy
from .variables_ui import STARTUP_BL_IDNAME, STARTUP_LABEL

class REOM_VC_OT_startup(bpy.types.Operator):
    bl_idname = STARTUP_BL_IDNAME
    bl_label = STARTUP_LABEL
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)
    
    def draw(self, context):
        self.layout.label(text="Version Control is ready.")
        prefs = context.preferences.addons[__package__].preferences
        self.layout.prop(prefs, "lib_path")
    
    def execute(self, context):
        return {'FINISHED'}