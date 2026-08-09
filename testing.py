import bpy
from .variables import DEFAULT_URL, DEFAULT_AUTO_UPDATE, DEFAULT_VERSION, MIN_VERSION
from .variables_ui import (
    THING_BL_IDNAME, THING_LABEL,
    NOTIFY_BL_IDNAME, NOTIFY_LABEL,
    POPUP_MENU_BL_IDNAME, POPUP_MENU_LABEL, POPUP_MESSAGE,
    POPUP_BL_IDNAME, POPUP_LABEL,
    CONFIRM_BL_IDNAME, CONFIRM_LABEL,
    SETTINGS_BL_IDNAME, SETTINGS_LABEL,
)

class MY_OT_thing(bpy.types.Operator):
    bl_idname = THING_BL_IDNAME
    bl_label = THING_LABEL
    
    def execute(self, context):
        print("done")
        return {'FINISHED'}

class MY_OT_notify(bpy.types.Operator):
    bl_idname = NOTIFY_BL_IDNAME
    bl_label = NOTIFY_LABEL

    def execute(self, context):
        self.report({'INFO'}, "Asset library downloaded!")
        return {'FINISHED'}

class MY_MT_popup(bpy.types.Menu):
    bl_idname = POPUP_MENU_BL_IDNAME
    bl_label = POPUP_MENU_LABEL
    
    def draw(self, context):
        self.layout.label(text=POPUP_MESSAGE)
        self.layout.operator(THING_BL_IDNAME)

class MY_OT_popup(bpy.types.Operator):
    bl_idname = POPUP_BL_IDNAME
    bl_label = POPUP_LABEL
    
    def execute(self, context):
        bpy.ops.wm.call_menu(name=POPUP_MENU_BL_IDNAME)
        return {'FINISHED'}

class MY_OT_confirm(bpy.types.Operator):
    bl_idname = CONFIRM_BL_IDNAME
    bl_label = CONFIRM_LABEL
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
    def execute(self, context):
        print("User clicked OK")
        return {'FINISHED'}

class MY_OT_settings(bpy.types.Operator):
    bl_idname = SETTINGS_BL_IDNAME
    bl_label = SETTINGS_LABEL
    
    url: bpy.props.StringProperty(name="URL", default=DEFAULT_URL)
    auto_update: bpy.props.BoolProperty(name="Auto-update", default=DEFAULT_AUTO_UPDATE)
    version: bpy.props.IntProperty(name="Version", default=DEFAULT_VERSION, min=MIN_VERSION)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "url")
        layout.prop(self, "auto_update")
        layout.prop(self, "version")
        
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)
    
    def execute(self, context):
        print(f"URL: {self.url}")
        print(f"Auto: {self.auto_update}")
        return {'FINISHED'}