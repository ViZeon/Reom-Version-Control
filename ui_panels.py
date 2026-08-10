import bpy
from . import functions, wrapper, data

def update_storage_mode(self, context):
    """Callback to trigger migration when the preference changes."""
    root = self.lib_path
    if root:
        functions.migrate_all_versions(root, self.storage_mode)

class ReomPrefs(bpy.types.AddonPreferences):
    bl_idname = __package__
    lib_path: bpy.props.StringProperty(name=data.TEXT_PREF_LIB, subtype=data.SUBTYPE_DIR)
    storage_mode: bpy.props.EnumProperty(
        items=data.ITEM_STORAGE_MODES, 
        default=data.MODE_SUB, 
        name=data.TEXT_PREF_STORAGE,
        update=update_storage_mode
    )
    
    def draw(self, ctx):
        self.layout.prop(self, data.PREF_LIB)
        self.layout.prop(self, data.PREF_STORAGE)

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
        
        lib = functions.get_lib(obj)
        
        if not lib:
            l.label(text=data.TEXT_SETUP_PROMPT)
            l.label(text=data.TEXT_SETUP_HINT)
            l.operator(data.OP_SETUP)
            return
        
        name = functions.get_name(obj)
        ver = functions.get_ver(obj)
        cat = functions.get_cat_name(obj)
        linked = functions.is_linked(obj)
        
        l.label(text=f"{data.TEXT_MESH}{name}")
        if ver: l.label(text=f"{data.TEXT_VERSION}{functions.format_ver_ui(ver)}")
        if cat: l.label(text=f"{data.TEXT_CAT}{cat}")
        
        l.prop(wrapper.get_prefs(), data.PREF_STORAGE, text="")
        
        if linked:
            l.box().label(text=data.TEXT_STATE_LINKED)
            l.operator(data.OP_ENTER_EDIT)
        else:
            l.box().label(text=data.TEXT_STATE_ACTIVE)
            row = l.row(align=True)
            op = row.operator(data.OP_VERSION, text=data.TEXT_SAVE)
            op.action = data.ACT_SAVE
            op = row.operator(data.OP_VERSION, text=data.TEXT_STEP)
            op.action = data.ACT_STEP
            op = row.operator(data.OP_VERSION, text=data.TEXT_RELEASE)
            op.action = data.ACT_RELEASE
            
            l.operator(data.OP_END_EDIT)
            
        vers = functions.scan_versions(name, wrapper.get_prefs().lib_path)
        if vers:
            l.label(text=data.TEXT_VERSIONS)
            box = l.box()
            for v in vers:
                row = box.row()
                row.label(text=functions.format_ver_ui(v))
                op = row.operator(data.OP_SET_MAIN, text=data.TEXT_SET_MAIN)
                op.version_str = functions.str_ver(v)
                
        l.separator()
        l.operator(data.OP_RUN_TESTS)