import bpy
from .variables_ui import PANEL_LABEL, PANEL_ID, PANEL_CATEGORY

class ReomVCPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    lib_path: bpy.props.StringProperty(name="Library Path", subtype='DIR_PATH')
    
    def draw(self, context):
        self.layout.prop(self, "lib_path")

class REOM_VC_PT_main(bpy.types.Panel):
    bl_label = PANEL_LABEL
    bl_idname = PANEL_ID
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = PANEL_CATEGORY
    
    def draw(self, context):
        self.layout.label(text="Reom Version Control")