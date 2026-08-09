import sys
import bpy
from .registry import classes
from .variables import FIRST_RUN_DELAY
from .variables_ui import STARTUP_BL_IDNAME

def find_view3d_area(context):
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                return (window, area)
    return (None, None)

def _invoke_operator(bl_idname):
    parts = bl_idname.split('.')
    op = bpy.ops
    for part in parts:
        op = getattr(op, part)
    op('INVOKE_DEFAULT')

def addon_register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    mod = sys.modules.get(__package__)
    auto_enabled = mod and getattr(mod, '_AUTO_ENABLED_BY_REOM_EXT', False)
    
    if auto_enabled:
        mod._AUTO_ENABLED_BY_REOM_EXT = False
    else:
        def _startup():
            window, area = find_view3d_area(bpy.context)
            if window and area:
                with bpy.context.temp_override(window=window, area=area):
                    _invoke_operator(STARTUP_BL_IDNAME)
            return None
        bpy.app.timers.register(_startup, first_interval=FIRST_RUN_DELAY)

def addon_unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)