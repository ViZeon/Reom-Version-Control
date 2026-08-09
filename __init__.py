bl_info = {
    "name": "Reom Version Control",
    "version": (1, 0, 0),
    "blender": (5, 2, 0),
    "category": "Generic",
}

from .funcs import addon_register, addon_unregister

def register():
    addon_register()

def unregister():
    addon_unregister()