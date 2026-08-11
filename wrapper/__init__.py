"""Thin Blender API adapters. No logic."""
import bpy
from .. import data

addon_keymaps = []

def register(classes):
    for c in classes: bpy.utils.register_class(c)

def unregister(classes):
    for c in reversed(classes): bpy.utils.unregister_class(c)

def get_prefs(): return bpy.context.preferences.addons[__package__.split('.')[0]].preferences
def get_active_obj(): return bpy.context.active_object
def get_all_objs(): return bpy.data.objects
def get_meshes(): return bpy.data.meshes
def get_prop(obj, key): return obj.get(key)
def set_prop(obj, key, val): obj[key] = val
def has_asset(obj): return obj.asset_data is not None

# --- DRY HELPER: Gathers all dependencies for saving ---
def get_blocks(objs):
    blocks = set()
    if not isinstance(objs, (list, set, tuple)): objs = [objs]
    for obj in objs:
        blocks.add(obj)
        if obj.data: 
            blocks.add(obj.data)
            blocks.update(m for m in obj.data.materials if m)
    return blocks

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

# --- MEMORY LEAK FIX: Purge orphan meshes ---
def remove_obj(obj): 
    mesh = obj.data
    bpy.data.objects.remove(obj, do_unlink=data.DO_UNLINK)
    if mesh and mesh.users == 0:
        bpy.data.meshes.remove(mesh, do_unlink=True)

def save_main(path): bpy.ops.wm.save_as_mainfile(filepath=path, copy=data.COPY_MAIN)
def abspath(p): return bpy.path.abspath(p)

def is_linked(obj):
    return bool(obj and (obj.library or (obj.data and obj.data.library)))

def make_local(obj):
    obj.make_local()
    if obj.data: 
        obj.data.make_local()
        for mat in obj.data.materials: mat.make_local()
    if obj.asset_data: obj.asset_clear()

def link_obj_from_lib(lib_path, name):
    if name not in bpy.data.objects:
        with bpy.data.libraries.load(lib_path, link=True) as (df, dt):
            if name in df.objects: dt.objects = [name]
            
    obj = bpy.data.objects.get(name)
    if obj:
        if obj.name not in bpy.context.collection.objects:
            bpy.context.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

def register_keymap(op_id, key, mods, prop_name=None, prop_val=None):
    wm = bpy.context.window_manager
    if not wm.keyconfigs.addon: return
    km = wm.keyconfigs.addon.keymaps.get("3D View") or wm.keyconfigs.addon.keymaps.new(name="3D View", space_type='VIEW_3D', region_type='WINDOW')
    kmi = km.keymap_items.new(op_id, key, 'PRESS', shift=data.MOD_SHIFT in mods, alt=data.MOD_ALT in mods, ctrl=data.MOD_CTRL in mods)
    if prop_name and prop_val: setattr(kmi.properties, prop_name, prop_val)
    addon_keymaps.append((km, kmi))

def unregister_keymaps():
    wm = bpy.context.window_manager
    if not wm.keyconfigs.addon: return
    for km, kmi in addon_keymaps:
        try: km.keymap_items.remove(kmi)
        except: pass
    addon_keymaps.clear()

def refresh_assets():
    def _refresh():
        for w in bpy.context.window_manager.windows:
            for a in w.screen.areas:
                if a.type == 'ASSETS':
                    with bpy.context.temp_override(window=w, area=a):
                        bpy.ops.asset.library_refresh()
        return None
    bpy.app.timers.register(_refresh, first_interval=data.REFRESH_DELAY)
