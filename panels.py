import bpy
from .variables_ui import (
    PANEL_LABEL, PANEL_ID, PANEL_CATEGORY,
    THING_BL_IDNAME, POPUP_BL_IDNAME, CONFIRM_BL_IDNAME, SETTINGS_BL_IDNAME,
)

class MY_PT_thing(bpy.types.Panel):
    bl_label = PANEL_LABEL
    bl_idname = PANEL_ID
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = PANEL_CATEGORY
    
    def draw(self, context):
        self.layout.operator(THING_BL_IDNAME)
        self.layout.operator(POPUP_BL_IDNAME)
        self.layout.operator(CONFIRM_BL_IDNAME)
        self.layout.operator(SETTINGS_BL_IDNAME)