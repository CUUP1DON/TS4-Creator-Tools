import bpy
import os
from bpy.types import Operator
from bpy.props import EnumProperty
from .ci_asset_management import (
    get_custom_assets_path, 
    get_asset_items, 
    show_popup
)

class TSCT_OT_load_custom_cas(Operator):
    """Load a custom CAS part"""
    bl_idname = "tsct.load_custom_cas"
    bl_label = "Load a Custom CAS Part"
    bl_description = "Load a custom CAS part."
    bl_options = {'REGISTER', 'UNDO'}
    
    def get_cas_items(self, context):
        return get_asset_items("CAS")
    
    cas_part: EnumProperty(
        name="Custom CAS Part", 
        description="Select a custom CAS part to load.", 
        items=get_cas_items
    )
    
    def invoke(self, context, event):
        items = get_asset_items("CAS")
        if len(items) == 1 and items[0][0] == 'NONE':
            show_popup("No custom CAS parts found.", icon='ERROR')
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        if self.cas_part == 'NONE':
            return {'CANCELLED'}
        
        bpy.ops.ed.undo_push(message="Creator Tools: Load Custom CAS")
        
        file_path = os.path.join(get_custom_assets_path(), "CAS", self.cas_part)
        
        if not os.path.exists(file_path):
            show_popup(f"File not found: {self.cas_part}", icon='ERROR')
            return {'CANCELLED'}
        
        return self.load_file(context, file_path, "CAS")

    def load_file(self, context, blend_path, asset_type):
        """Load blend file similar to body base loader pattern"""
        try:
            # Get the asset name from filename (without .blend)
            asset_name = os.path.basename(blend_path)[:-6]
            
            print(f"Loading {asset_name} from: {blend_path}")
            
            # Load the blend file
            with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
                # Debug: Print all available objects
                print(f"Available objects in {os.path.basename(blend_path)}: {list(data_from.objects)}")
                
                # Load all objects and materials
                data_to.objects = data_from.objects if data_from.objects else []
                data_to.materials = data_from.materials if data_from.materials else []
            
            # Add loaded objects to the scene
            loaded_objects = []
            for obj in data_to.objects:
                if obj is not None and obj.type not in {'CAMERA', 'LIGHT'}:
                    context.collection.objects.link(obj)
                    obj.select_set(True)
                    loaded_objects.append(obj)
            
            if loaded_objects:
                context.view_layer.objects.active = loaded_objects[0]
                success_msg = f"Custom CAS part '{asset_name}' loaded successfully. Loaded {len(loaded_objects)} objects."
                show_popup(success_msg)
                return {'FINISHED'}
            else:
                show_popup("No valid objects were loaded from the file.", icon='ERROR')
                return {'CANCELLED'}
            
        except Exception as e:
            show_popup(f"Error loading Custom CAS: {str(e)}", icon='ERROR')
            print(f"Full error details: {e}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}

# Registration
classes = [
    TSCT_OT_load_custom_cas,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)