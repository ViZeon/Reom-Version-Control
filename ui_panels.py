import bpy
from . import functions, wrapper, data

class ReomPrefs(bpy.types.AddonPreferences):
    bl_idname = __package__
    lib_path: bpy.props.StringProperty(name="Library Path", subtype=data.SUBTYPE_DIR)
    
    def draw(self, ctx):
        self.layout.prop(self, data.PREF_LIB)

class REOM_VC_PT_main(bpy.types.Panel):
    bl_label = data.PANEL_LABEL
    bl_idname = data.PANEL_ID
    bl_space_type = data.AREA_VIEW3D
    bl_region_type = data.REGION_UI
    bl_category = data.PANEL_CATEGORY

    def draw(self, ctx):
        l = self.layout
        obj = wrapper.get_active_obj()
        if not obj: return
        
        name = functions.get_name(obj)
        ver = functions.get_ver(obj)
        cat = functions.get_cat_name(obj)
        
        l.label(text=f"{data.TEXT_MESH}{name}")
        if ver: l.label(text=f"{data.TEXT_VERSION}{functions.str_ver(ver)}")
        if cat: l.label(text=f"{data.TEXT_CAT}{cat}")
        
        vers = functions.scan_versions(name, wrapper.get_prefs().lib_path)
        if vers:
            l.label(text=data.TEXT_VERSIONS)
            box = l.box()
            for v in vers:
                row = box.row()
                row.label(text=functions.str_ver(v))
                op = row.operator(data.OP_HIGHLIGHT, text=data.TEXT_HIGHLIGHT)
                op.version_str = functions.str_ver(v)
        
        l.operator(data.OP_TEST)
        l.operator(data.OP_SAVE)
        l.operator(data.OP_HIGHLIGHT)
        l.operator(data.OP_SETUP_CAT)