import bpy

class MY_PT_thing(bpy.types.Panel):
    bl_label = "My Panel"
    bl_idname = "VIEW3D_PT_my_thing"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MyTab"
    
    def draw(self, context):
        self.layout.operator("my.thing")
        self.layout.operator("my.popup")
        self.layout.operator("my.confirm")
        self.layout.operator("my.settings")