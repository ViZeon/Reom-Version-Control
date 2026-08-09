"""All Blender API calls live here. funcs.py never imports bpy."""

import bpy

# === REGISTRATION ===
def class_register(cls):
    bpy.utils.register_class(cls)

def class_unregister(cls):
    bpy.utils.unregister_class(cls)

def classes_register(class_list):
    for cls in class_list:
        class_register(cls)

def classes_unregister(class_list):
    for cls in reversed(class_list):
        class_unregister(cls)

# === CONTEXT QUERIES ===
def context_get_windows():
    return bpy.context.window_manager.windows

def context_get_view3d_area():
    for window in context_get_windows():
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                return (window, area)
    return (None, None)

def context_get_addon_preferences(module_name):
    return bpy.context.preferences.addons[module_name].preferences

def context_get_active_object():
    return bpy.context.active_object

# === OPERATOR INVOCATION ===
def operator_invoke(bl_idname):
    parts = bl_idname.split('.')
    op = bpy.ops
    for part in parts:
        op = getattr(op, part)
    op('INVOKE_DEFAULT')

# === ADDON MANAGEMENT ===
def addon_is_enabled(module_name):
    return module_name in bpy.context.preferences.addons

# === TIMERS ===
def timer_register(callback, delay):
    bpy.app.timers.register(callback, first_interval=delay)

# === CONTEXT OVERRIDES ===
def context_temp_override(window, area):
    return bpy.context.temp_override(window=window, area=area)

# === OBJECT PROPERTIES ===
def object_get_property(obj, key):
    return obj.get(key, None)

def object_set_property(obj, key, value):
    obj[key] = value