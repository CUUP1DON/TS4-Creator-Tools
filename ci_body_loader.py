import bpy
from bpy.props import EnumProperty
from .ci_base_loader import BaseCustomLoader
from .ci_asset_management import get_asset_items

class TSCT_OT_load_custom_body(BaseCustomLoader):
    """Load custom body"""
    bl_idname = "tsct.load_custom_body"
    bl_label = "Load Custom Body"
    bl_description = "Load a custom body."
    
    def get_body_items(self, context):
        return get_asset_items("Body")
    
    body_item: EnumProperty(
        name="Custom Body", 
        description="Select a custom body to load", 
        items=get_body_items
    )
    
    def invoke(self, context, event):
        return self.invoke_with_check(context, "Body")
    
    def execute(self, context):
        return self.execute_load(context, "Body", "body_item")

# Registration
classes = [
    TSCT_OT_load_custom_body,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)