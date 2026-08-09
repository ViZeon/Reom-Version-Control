import bpy

class MY_OT_thing(bpy.types.Operator):
    bl_idname = "my.thing"
    bl_label = "Do Thing"
    
    def execute(self, context):
        print("done")
        return {'FINISHED'}

class MY_OT_notify(bpy.types.Operator):
    bl_idname = "my.notify"
    bl_label = "Notify"

    def execute(self, context):
        self.report({'INFO'}, "Asset library downloaded!")
        return {'FINISHED'}

class MY_MT_popup(bpy.types.Menu):
    bl_idname = "my.popup_menu"
    bl_label = "Confirm Download"
    
    def draw(self, context):
        self.layout.label(text="Download 50MB asset library?")
        self.layout.operator("my.thing")

class MY_OT_popup(bpy.types.Operator):
    bl_idname = "my.popup"
    bl_label = "Show Popup"
    
    def execute(self, context):
        bpy.ops.wm.call_menu(name="my.popup_menu")
        return {'FINISHED'}


class MY_OT_confirm(bpy.types.Operator):
    bl_idname = "my.confirm"
    bl_label = "Delete everything?"
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
    def execute(self, context):
        print("User clicked OK")
        return {'FINISHED'}

class MY_OT_settings(bpy.types.Operator):
    bl_idname = "my.settings"
    bl_label = "Download Settings"
    
    # Input fields
    url: bpy.props.StringProperty(name="URL", default="https://github.com/...")
    auto_update: bpy.props.BoolProperty(name="Auto-update", default=True)
    version: bpy.props.IntProperty(name="Version", default=1, min=1)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "url")
        layout.prop(self, "auto_update")
        layout.prop(self, "version")
        
    def invoke(self, context, event):
        # This opens the blocking dialog
        return context.window_manager.invoke_props_dialog(self, width=300)
    
    def execute(self, context):
        print(f"URL: {self.url}")
        print(f"Auto: {self.auto_update}")
        return {'FINISHED'}