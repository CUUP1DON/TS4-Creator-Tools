import bpy
import os
from bpy.types import Operator
from bpy.props import EnumProperty
from .ci_asset_management import (
    get_custom_assets_path, 
    get_asset_items, 
    show_popup,
    get_or_create_collection,
    find_root_collections
)

class BaseCustomLoader(Operator):
    """Base class for custom asset loaders"""
    bl_options = {'REGISTER', 'UNDO'}
    
    def invoke_with_check(self, context, asset_type):
        """Common invoke logic with asset check"""
        items = get_asset_items(asset_type)
        if len(items) == 1 and items[0][0] == 'NONE':
            show_popup(f"No custom {asset_type.lower()} found.", icon='ERROR')
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self)
    
    def execute_load(self, context, asset_type, item_prop):
        """Common execute logic"""
        if getattr(self, item_prop) == 'NONE':
            return {'CANCELLED'}
        
        bpy.ops.ed.undo_push(message=f"Creator Tools: Load Custom {asset_type}")
        
        file_path = os.path.join(get_custom_assets_path(), asset_type, getattr(self, item_prop))
        
        if not os.path.exists(file_path):
            show_popup(f"File not found: {getattr(self, item_prop)}", icon='ERROR')
            return {'CANCELLED'}
        
        return self.load_file(context, file_path, asset_type)
    
    def load_file(self, context, blend_path, asset_type):
        """Load blend file with appropriate handling based on asset type"""
        try:
            # Get the asset name from filename (without .blend)
            asset_name = os.path.basename(blend_path)[:-6]
            
            # Create or get the main Custom Assets collection
            main_collection = get_or_create_collection("Custom Assets")
            
            # Create or get the asset type collection
            type_collection = get_or_create_collection(f"Custom {asset_type}", main_collection)
            
            # Load the blend file
            with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
                print(f"Available objects in {os.path.basename(blend_path)}: {list(data_from.objects)}")
                print(f"Available collections in {os.path.basename(blend_path)}: {list(data_from.collections)}")
                
                # Load all available data
                data_to.objects = data_from.objects if data_from.objects else []
                data_to.materials = data_from.materials if data_from.materials else []
                data_to.collections = data_from.collections if data_from.collections else []
                
                # Load additional data for specific asset types
                if asset_type in ["Rig"] and hasattr(data_from, 'armatures') and data_from.armatures:
                    data_to.armatures = data_from.armatures
            
            # Now process what was loaded
            loaded_objects = []
            special_objects = []
            imported_collections = []
            target_collection = None
            
            # Handle collections
            if data_to.collections:
                # Find only the root collections (not nested ones)
                root_collections = find_root_collections(data_to.collections)
                
                for collection in root_collections:
                    if collection is not None:
                        # Remove from scene collection if it was auto-linked there
                        scene_collection = bpy.context.scene.collection
                        if collection.name in [child.name for child in scene_collection.children]:
                            scene_collection.children.unlink(collection)
                        
                        # Link only the root collection to our type collection
                        type_collection.children.link(collection)
                        imported_collections.append(collection)
                        if target_collection is None:
                            target_collection = collection
                        print(f"Imported root collection '{collection.name}' to {type_collection.name}")
                
                # Process objects - they should already be properly organized in their collections
                for obj in data_to.objects:
                    if obj is not None and obj.type not in {'CAMERA', 'LIGHT'}:
                        obj.select_set(True)
                        loaded_objects.append(obj)
                        
                        if obj.type == 'ARMATURE':
                            special_objects.append(obj)
            else:
                # No collections in blend file - create our own and add objects to it
                target_collection = get_or_create_collection(asset_name, type_collection)
                
                for obj in data_to.objects:
                    if obj is not None and obj.type not in {'CAMERA', 'LIGHT'}:
                        target_collection.objects.link(obj)
                        obj.select_set(True)
                        loaded_objects.append(obj)
                        
                        if obj.type == 'ARMATURE':
                            special_objects.append(obj)
            
            if loaded_objects:
                # Set active object
                if special_objects:
                    context.view_layer.objects.active = special_objects[0]
                elif loaded_objects:
                    context.view_layer.objects.active = loaded_objects[0]
                
                # Build success message
                msg_parts = []
                if loaded_objects:
                    if asset_type == "Rig" and special_objects:
                        msg_parts.append(f"{len(special_objects)} armature(s)")
                        msg_parts.append(f"{len(loaded_objects)} total objects")
                    else:
                        msg_parts.append(f"{len(loaded_objects)} objects")
                
                if imported_collections:
                    msg_parts.append(f"{len(imported_collections)} root collections")
                
                collection_name = target_collection.name if target_collection else "scene"
                success_msg = f"Custom {asset_type} '{asset_name}' loaded successfully. Loaded " + ", ".join(msg_parts) + f" in collection '{collection_name}'."
                
                show_popup(success_msg)
                return {'FINISHED'}
            else:
                show_popup("No valid objects were loaded from the file.", icon='ERROR')
                return {'CANCELLED'}
            
        except Exception as e:
            show_popup(f"Error loading Custom {asset_type}: {str(e)}", icon='ERROR')
            print(f"Full error details: {e}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}

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