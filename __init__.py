bl_info = {
    "name": "Reom Version Control",
    "version": (1, 0, 0),
    "blender": (5, 2, 0),
    "category": "Generic",
}

from . import funcs
from . import registry

def register():
    funcs.addon_register(registry.classes)

def unregister():
    funcs.addon_unregister(registry.classes)