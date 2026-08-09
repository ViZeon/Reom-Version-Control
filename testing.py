"""Playground operators. Experiment here."""

import bpy
from . import blender_api, funcs
from .variables_ui import TEST_SCAN_BL_IDNAME, TEST_SCAN_LABEL

class REOM_VC_OT_test_scan(bpy.types.Operator):
    bl_idname = TEST_SCAN_BL_IDNAME
    bl_label = TEST_SCAN_LABEL
    
    def execute(self, context):
        obj = blender_api.context_get_active_object()
        if not obj:
            print("No active object selected")
            return {'CANCELLED'}
        
        mesh_name = funcs.mesh_get_name(obj)
        print(f"Mesh identity: {mesh_name}")
        
        prefs = context.preferences.addons[__package__].preferences
        lib_path = prefs.lib_path
        
        if not lib_path:
            print("No library path set in preferences")
            return {'CANCELLED'}
        
        versions = funcs.file_scan_versions(mesh_name, lib_path)
        versions.sort()
        
        if versions:
            ver_strings = [funcs.version_to_string(v) for v in versions]
            print(f"Mesh '{mesh_name}' has versions: {', '.join(ver_strings)}")
        else:
            print(f"Mesh '{mesh_name}' has no versions in library")
        
        return {'FINISHED'}