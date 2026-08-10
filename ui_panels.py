import bpy
from . import functions, wrapper
from . import data

class ReomVCPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__
    lib_path: bpy.props.StringProperty(name=data.PREF_LABEL_LIB_PATH, subtype='DIR_PATH')
    tags: bpy.props.StringProperty(name=data.PREF_LABEL_TAGS, default=data.DEFAULT_TAGS)
    
    def draw(self, context):
        self.layout.prop(self, data.PREF_PROP_LIB_PATH)
        self.layout.prop(self, data.PREF_PROP_TAGS)

class REOM_VC_PT_main(bpy.types.Panel):
    bl_label = data.PANEL_LABEL
    bl_idname = data.PANEL_ID
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = data.PANEL_CATEGORY
    
    def draw(self, context):
        self.layout.label(text=data.PANEL_TEXT)
        
        obj = wrapper.get_active_object()
        if obj:
            mesh_name = functions.mesh_get_name(obj)
            current_ver = functions.mesh_get_version(obj)
            tag = functions.mesh_get_tag(obj)
            
            self.layout.label(text=f"Mesh: {mesh_name}")
            if current_ver:
                self.layout.label(text=f"Version: {functions.version_to_string(current_ver)}")
            if tag:
                self.layout.label(text=f"Tag: {tag}")
            
            prefs = context.preferences.addons[__package__].preferences
            versions = functions.file_scan_versions(mesh_name, prefs.lib_path)
            
            if versions:
                self.layout.label(text="Versions:")
                box = self.layout.box()
                for ver in versions:
                    ver_str = functions.version_to_string(ver)
                    row = box.row()
                    row.label(text=ver_str)
                    op = row.operator(data.OP_HIGHLIGHT_ID, text="Highlight")
                    op.version_str = ver_str
        
        self.layout.operator(data.OP_TEST_SCAN_ID)
        self.layout.operator(data.OP_SAVE_ID)
        self.layout.operator(data.OP_HIGHLIGHT_ID)
        self.layout.operator(data.OP_SET_TAG_ID)