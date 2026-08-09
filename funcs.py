import bpy
from .registry import classes
from .variables import FIRST_RUN_DELAY
from .variables_ui import SETTINGS_BL_IDNAME

def find_view3d_area(context):
    """Pure function. Returns (window, area) or (None, None)."""
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                return (window, area)
    return (None, None)

def _invoke_operator(bl_idname):
    """Takes 'my.settings', calls bpy.ops.my.settings('INVOKE_DEFAULT')."""
    parts = bl_idname.split('.')
    op = bpy.ops
    for part in parts:
        op = getattr(op, part)
    op('INVOKE_DEFAULT')

def addon_register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    def _first_run():
        window, area = find_view3d_area(bpy.context)
        if window and area:
            with bpy.context.temp_override(window=window, area=area):
                _invoke_operator(SETTINGS_BL_IDNAME)
        return None
    
    bpy.app.timers.register(_first_run, first_interval=FIRST_RUN_DELAY)

def addon_unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)