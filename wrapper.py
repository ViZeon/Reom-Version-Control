"""Thin Blender API adapters. No logic. Just translates."""

import bpy

# === REGISTRATION ===
def register_classes(class_list):
    for cls in class_list: bpy.utils.register_class(cls)

def unregister_classes(class_list):
    for cls in reversed(class_list): bpy.utils.unregister_class(cls)

# === CONTEXT & PREFS ===
def get_prefs():
    return bpy.context.preferences.addons[__package__].preferences

def get_active_object():
    return bpy.context.active_object

def get_all_objects():
    return bpy.data.objects

def get_view3d_context():
    for win in bpy.context.window_manager.windows:
        for area in win.screen.areas:
            if area.type == 'VIEW_3D':
                return win, area
    return None, None

def temp_override(window, area):
    return bpy.context.temp_override(window=window, area=area)

# === OPERATORS & TIMERS ===
def invoke_operator(bl_idname):
    ns, name = bl_idname.split('.')
    getattr(getattr(bpy.ops, ns), name)('INVOKE_DEFAULT')

def register_timer(callback, delay):
    bpy.app.timers.register(callback, first_interval=delay)

# === OBJECT PROPERTIES ===
def get_property(obj, key): 
    return obj.get(key, None)

def set_property(obj, key, value): 
    obj[key] = value

def has_asset_data(obj):
    return obj.asset_data is not None

def get_mesh_materials(obj):
    return [m for m in obj.data.materials] if obj.data else []

# === ASSET SYSTEM ===
def mark_asset(obj): 
    obj.asset_mark()

def set_asset_catalog(obj, catalog_id):
    if obj.asset_data: 
        obj.asset_data.catalog_id = catalog_id

# === DATA LIBRARIES ===
def write_libraries(filepath, blocks): 
    bpy.data.libraries.write(filepath, blocks, fake_user=True)

def load_library(filepath, link=False): 
    return bpy.data.libraries.load(filepath, link=link)

def remove_object(obj): 
    bpy.data.objects.remove(obj, do_unlink=True)

# === FILE OPERATIONS ===
def save_as_mainfile(filepath): 
    bpy.ops.wm.save_as_mainfile(filepath=filepath, copy=True)

def abspath(path): 
    return bpy.path.abspath(path)