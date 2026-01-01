import bpy
from bpy.props import EnumProperty
from .ci_base_loader import BaseCustomLoader
from .ci_asset_management import get_asset_items

class TSCT_OT_load_custom_rig(BaseCustomLoader):
    """Load custom rig"""
    bl_idname = "tsct.load_custom_rig"
    bl_label = "Load Custom Rig"
    bl_description = "Load a custom rig."

    # Exclude cameras and lights when loading rigs
    exclude_object_types = {'CAMERA', 'LIGHT'}

    def get_rig_items(self, context):
        return get_asset_items("Rig")
    
    rig_item: EnumProperty(
        name="Custom Rig", 
        description="Select a custom rig to load", 
        items=get_rig_items
    )
    
    def invoke(self, context, event):
        return self.invoke_with_check(context, "Rig")
    
    def execute(self, context):
        return self.execute_load(context, "Rig", "rig_item")

# Registration
classes = [
    TSCT_OT_load_custom_rig,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)