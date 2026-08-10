"""Thin Blender API adapters. No logic."""
import bpy

def register(classes):
    for c in classes: bpy.utils.register_class(c)

def unregister(classes):
    for c in reversed(classes): bpy.utils.unregister_class(c)

def get_prefs(): return bpy.context.preferences.addons[__package__].preferences
def get_active_obj(): return bpy.context.active_object
def get_all_objs(): return bpy.data.objects

def get_view3d():
    for w in bpy.context.window_manager.windows:
        for a in w.screen.areas:
            if a.type == 'VIEW_3D': return w, a
    return None, None

def invoke(op_id):
    ns, n = op_id.split('.')
    getattr(getattr(bpy.ops, ns), n)('INVOKE_DEFAULT')

def timer(cb, t): bpy.app.timers.register(cb, first_interval=t)
def override(win, area): return bpy.context.temp_override(window=win, area=area)

def get_prop(obj, key): return obj.get(key)
def set_prop(obj, key, val): obj[key] = val
def has_asset(obj): return obj.asset_data is not None
def get_mats(obj): return [m for m in obj.data.materials] if obj.data else []

def mark_asset(obj): obj.asset_mark()
def set_catalog(obj, cid): 
    if obj.asset_data: obj.asset_data.catalog_id = cid

def write_lib(path, blocks): bpy.data.libraries.write(path, blocks, fake_user=True)
def load_lib(path): return bpy.data.libraries.load(path)
def remove_obj(obj): bpy.data.objects.remove(obj, do_unlink=True)
def save_main(path): bpy.ops.wm.save_as_mainfile(filepath=path, copy=True)
def abspath(p): return bpy.path.abspath(p)