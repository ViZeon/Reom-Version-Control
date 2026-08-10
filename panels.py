import bpy
from . import funcs, blender_api
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
        
        obj = blender_api.context_get_active_object()
        if obj:
            mesh_name = funcs.mesh_get_name(obj)
            current_ver = funcs.mesh_get_version(obj)
            tag = funcs.mesh_get_tag(obj)
            
            self.layout.label(text=f"Mesh: {mesh_name}")
            if current_ver:
                self.layout.label(text=f"Version: {funcs.version_to_string(current_ver)}")
            if tag:
                self.layout.label(text=f"Tag: {tag}")
            
            prefs = context.preferences.addons[__package__].preferences
            versions = funcs.file_scan_versions(mesh_name, prefs.lib_path)
            versions.sort()
            
            if versions:
                self.layout.label(text="Versions:")
                box = self.layout.box()
                for ver in versions:
                    ver_str = funcs.version_to_string(ver)
                    row = box.row()
                    row.label(text=ver_str)
                    op = row.operator(HIGHLIGHT_BL_IDNAME, text="Highlight")
                    op.version_str = ver_str
        
        self.layout.operator(TEST_SCAN_BL_IDNAME)
        self.layout.operator(SAVE_BL_IDNAME)
        self.layout.operator(HIGHLIGHT_BL_IDNAME)
        self.layout.operator(SET_TAG_BL_IDNAME)