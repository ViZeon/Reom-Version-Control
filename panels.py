import bpy
from .variables_ui import (
    PANEL_LABEL, PANEL_ID, PANEL_CATEGORY, PANEL_TEXT,
    PROP_NAME_LIB_PATH, PROP_NAME_TAGS,
    TEST_SCAN_BL_IDNAME, SAVE_BL_IDNAME,
    HIGHLIGHT_BL_IDNAME, SET_TAG_BL_IDNAME,
)

class ReomVCPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    lib_path: bpy.props.StringProperty(name=PROP_NAME_LIB_PATH, subtype='DIR_PATH')
    tags: bpy.props.StringProperty(name=PROP_NAME_TAGS, default="Character, Prop, Weapon")
    
    def draw(self, context):
        self.layout.prop(self, "lib_path")
        self.layout.prop(self, "tags")

class REOM_VC_PT_main(bpy.types.Panel):
    bl_label = PANEL_LABEL
    bl_idname = PANEL_ID
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = PANEL_CATEGORY
    
    def draw(self, context):
        self.layout.label(text=PANEL_TEXT)
        self.layout.operator(TEST_SCAN_BL_IDNAME)
        self.layout.operator(SAVE_BL_IDNAME)
        self.layout.operator(HIGHLIGHT_BL_IDNAME)
        self.layout.operator(SET_TAG_BL_IDNAME)