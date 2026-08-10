"""Thin Blender API adapters. Translates Blender types to plain data. No logic."""

import bpy

# === REGISTRATION ===
def register_class(cls):
    bpy.utils.register_class(cls)

def unregister_class(cls):
    bpy.utils.unregister_class(cls)

def register_classes(class_list):
    for cls in class_list:
        register_class(cls)

def unregister_classes(class_list):
    for cls in reversed(class_list):
        unregister_class(cls)

# === CONTEXT QUERIES ===
def get_windows():
    return bpy.context.window_manager.windows

def get_active_object():
    return bpy.context.active_object

def get_all_objects():
    return bpy.data.objects

def get_addon_preferences(module_name):
    return bpy.context.preferences.addons[module_name].preferences

# === CONTEXT OVERRIDES ===
def temp_override(window, area):
    return bpy.context.temp_override(window=window, area=area)

# === OPERATOR INVOCATION ===
def invoke_operator(bl_idname):
    parts = bl_idname.split('.')
    op = bpy.ops
    for part in parts:
        op = getattr(op, part)
    op('INVOKE_DEFAULT')

# === TIMERS ===
def register_timer(callback, delay):
    bpy.app.timers.register(callback, first_interval=delay)

# === OBJECT PROPERTIES ===
def get_property(obj, key):
    return obj.get(key, None)

def set_property(obj, key, value):
    obj[key] = value

# === ASSET SYSTEM ===
def mark_asset(obj):
    obj.asset_mark()

def set_asset_catalog(obj, catalog_id):
    if obj.asset_data:
        obj.asset_data.catalog_id = catalog_id

# === DATA LIBRARIES ===
def write_libraries(filepath, blocks, fake_user=True):
    bpy.data.libraries.write(filepath, blocks, fake_user=fake_user)

def load_library(filepath, link=False):
    return bpy.data.libraries.load(filepath, link=link)

def remove_object(obj):
    bpy.data.objects.remove(obj, do_unlink=True)

# === FILE OPERATIONS ===
def save_as_mainfile(filepath):
    bpy.ops.wm.save_as_mainfile(filepath=filepath, copy=True)

def abspath(path):
    return bpy.path.abspath(path)