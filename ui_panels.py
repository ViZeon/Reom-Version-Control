import bpy
from . import functions, wrapper, data

class ReomPrefs(bpy.types.AddonPreferences):
    bl_idname = __package__
    lib_path: bpy.props.StringProperty(name="Library Path", subtype='DIR_PATH')
    tags: bpy.props.StringProperty(name="Tags", default=data.DEFAULT_TAGS)
    
    def draw(self, ctx):
        self.layout.prop(self, "lib_path")
        self.layout.prop(self, "tags")

class REOM_VC_PT_main(bpy.types.Panel):
    bl_label = "Reom VC"
    bl_idname = data.PANEL_ID
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Reom"

    def draw(self, ctx):
        l = self.layout
        obj = wrapper.get_active_obj()
        if not obj: return
        
        name = functions.mesh_get_name(obj)
        ver = functions.mesh_get_ver(obj)
        tag = functions.mesh_get_tag(obj)
        
        l.label(text=f"Mesh: {name}")
        if ver: l.label(text=f"Version: {functions.ver_str(ver)}")
        if tag: l.label(text=f"Tag: {tag}")
        
        vers = functions.file_scan_versions(name, wrapper.get_prefs().lib_path)
        if vers:
            l.label(text="Versions:")
            box = l.box()
            for v in vers:
                row = box.row()
                row.label(text=functions.ver_str(v))
                op = row.operator(data.OP_HIGHLIGHT, text="Highlight")
                op.version_str = functions.ver_str(v)
        
        l.operator(data.OP_TEST)
        l.operator(data.OP_SAVE)
        l.operator(data.OP_HIGHLIGHT)
        l.operator(data.OP_TAG)