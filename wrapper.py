"""Thin Blender API adapters. No logic."""
import bpy
from . import data

def register(classes):
    for c in classes: bpy.utils.register_class(c)

def unregister(classes):
    for c in reversed(classes): bpy.utils.unregister_class(c)

def get_prefs(): return bpy.context.preferences.addons[__package__].preferences
def get_active_obj(): return bpy.context.active_object
def get_all_objs(): return bpy.data.objects
def get_meshes(): return bpy.data.meshes
def get_prop(obj, key): return obj.get(key)
def set_prop(obj, key, val): obj[key] = val
def has_asset(obj): return obj.asset_data is not None
def get_mats(obj): return [m for m in obj.data.materials] if obj.data else []

def get_view3d():
    for w in bpy.context.window_manager.windows:
        for a in w.screen.areas:
            if a.type == data.AREA_VIEW3D: return w, a
    return None, None

def invoke(op_id):
    ns, n = op_id.split('.')
    getattr(getattr(bpy.ops, ns), n)(data.OP_INVOKE)

def timer(cb, t): bpy.app.timers.register(cb, first_interval=t)
def override(win, area): return bpy.context.temp_override(window=win, area=area)

def mark_asset(obj): obj.asset_mark()
def clear_asset(obj): obj.asset_clear()
def set_catalog(obj, cid): 
    if obj.asset_data: obj.asset_data.catalog_id = cid

def write_lib(path, blocks): bpy.data.libraries.write(path, blocks, fake_user=data.FAKE_USER)
def load_lib(path): return bpy.data.libraries.load(path)
def remove_obj(obj): bpy.data.objects.remove(obj, do_unlink=data.DO_UNLINK)
def save_main(path): bpy.ops.wm.save_as_mainfile(filepath=path, copy=data.COPY_MAIN)
def abspath(p): return bpy.path.abspath(p)

# === OBJECT LINKING ===
def is_linked(obj):
    if not obj: return False
    if obj.library: return True
    if obj.data and obj.data.library: return True
    return False

def make_local(obj):
    obj.make_local()
    if obj.data: 
        obj.data.make_local()
        for mat in obj.data.materials: mat.make_local()
    if obj.asset_data: obj.asset_clear()

def link_obj_from_lib(lib_path, name):
    if name not in bpy.data.objects:
        with bpy.data.libraries.load(lib_path, link=True) as (df, dt):
            dt.objects = [name] if name in df.objects else []
            
    if name in bpy.data.objects:
        obj = bpy.data.objects[name]
        if obj.name not in bpy.context.collection.objects:
            bpy.context.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

# === ASSET BROWSER ===
def refresh_assets():
    """Force refresh all open Asset Browsers after a short delay to ensure file locks are released."""
    def _refresh():
        for w in bpy.context.window_manager.windows:
            for a in w.screen.areas:
                if a.type == 'ASSETS':
                    with bpy.context.temp_override(window=w, area=a):
                        bpy.ops.asset.library_refresh()
        return None
    bpy.app.timers.register(_refresh, first_interval=data.REFRESH_DELAY)