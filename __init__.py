bl_info = {
    "name": "Reom Version Control",
    "version": (1, 0, 0),
    "blender": (5, 2, 0),
    "category": "Generic",
}

import bpy
from .registry import classes

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Schedule the popup for after UI is ready
    bpy.app.timers.register(_first_run, first_interval=0.1)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

def _first_run():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                with bpy.context.temp_override(window=window, area=area):
                    bpy.ops.my.settings('INVOKE_DEFAULT')
                return None
    return None