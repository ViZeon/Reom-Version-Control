bl_info = {
    "name": "Reom Version Control",
    "version": (1, 0, 0),
    "blender": (5, 2, 0),
    "category": "Generic",
}

from . import functions
from .ui import registry

def register():
    functions.addon_register(registry.classes)

def unregister():
    functions.addon_unregister(registry.classes)