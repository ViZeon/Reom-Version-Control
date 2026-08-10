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
        layout = self.layout
        layout.label(text=data.PANEL_TEXT)
        
        obj = wrapper.get_active_object()
        if not obj: return
        
        mesh_name = functions.mesh_get_name(obj)
        ver = functions.mesh_get_version(obj)
        tag = functions.mesh_get_tag(obj)
        
        layout.label(text=f"Mesh: {mesh_name}")
        if ver: layout.label(text=f"Version: {functions.version_to_string(ver)}")
        if tag: layout.label(text=f"Tag: {tag}")
        
        vers = functions.file_scan_versions(mesh_name, wrapper.get_prefs().lib_path)
        if vers:
            layout.label(text="Versions:")
            box = layout.box()
            for v in vers:
                row = box.row()
                row.label(text=functions.version_to_string(v))
                op = row.operator(data.OP_HIGHLIGHT_ID, text="Highlight")
                op.version_str = functions.version_to_string(v)
        
        layout.operator(data.OP_TEST_SCAN_ID)
        layout.operator(data.OP_SAVE_ID)
        layout.operator(data.OP_HIGHLIGHT_ID)
        layout.operator(data.OP_SET_TAG_ID)