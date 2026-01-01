import bpy
import os
from bpy.types import Operator
from .ci_asset_management import show_popup

class TSCT_OT_load_body_base(Operator):
    bl_idname = "object.load_body_base"
    bl_label = "Load Body Base"
    bl_description = "Load a body base mesh"
    bl_options = {'REGISTER', 'UNDO'}
    
    body_type: bpy.props.EnumProperty(
        name="Body Type",
        description="Type of body base to load",
        items=[
            ('AM', 'Adult Male', 'Adult Male body type'),
            ('AF', 'Adult Female', 'Adult Female body type'),
            ('C', 'Child', 'Child body type'),
            ('T', 'Toddler', 'Toddler body type'),
            ('I', 'Infant', 'Infant body type'),
        ],
        default='AM'
    )
    
    mesh_type: bpy.props.EnumProperty(
        name="Mesh Type",
        description="Type of mesh to load",
        items=[
            ('Full', 'Full Body', 'Complete body mesh'),
            ('Head', 'Head', 'Head mesh only'),
            ('Top', 'Top', 'Upper body mesh only'),
            ('Bottom', 'Bottom', 'Lower body mesh only'),
            ('Feet', 'Feet', 'Feet mesh only')
        ],
        default='Full'
    )
    
    def invoke(self, context, event):
        # Force the dialog to appear
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Load Body Base")
        
        # Get the addon directory
        addon_dir = os.path.dirname(os.path.realpath(__file__))
        assets_dir = os.path.join(addon_dir, "assets")
        body_dir = os.path.join(assets_dir, "body")
        head_dir = os.path.join(body_dir, "head")
        feet_dir = os.path.join(body_dir, "feet")
        bottom_dir = os.path.join(body_dir, "bottom")
        top_dir = os.path.join(body_dir, "top")
        full_dir = os.path.join(body_dir, "full")
        
        # Construct the blend file path
        blend_file = f"{self.body_type}_{self.mesh_type}.blend"
        
        # Determine which directory to use based on mesh type
        if self.mesh_type == 'Head':
            blend_path = os.path.join(head_dir, blend_file)
            search_location = "head folder"
            fallback_dir = head_dir
        elif self.mesh_type == 'Feet':
            blend_path = os.path.join(feet_dir, blend_file)
            search_location = "feet folder"
            fallback_dir = feet_dir
        elif self.mesh_type == 'Bottom':
            blend_path = os.path.join(bottom_dir, blend_file)
            search_location = "bottom folder"
            fallback_dir = bottom_dir
        elif self.mesh_type == 'Top':
            blend_path = os.path.join(top_dir, blend_file)
            search_location = "top folder"
            fallback_dir = top_dir
        elif self.mesh_type == 'Full':
            blend_path = os.path.join(full_dir, blend_file)
            search_location = "full folder"
            fallback_dir = full_dir
        else:
            blend_path = os.path.join(assets_dir, blend_file)
            search_location = "assets folder"
            fallback_dir = None
        
        # Check if file exists
        if not os.path.exists(blend_path):
            # Try assets folder as fallback for organized mesh types
            if fallback_dir is not None:
                fallback_path = os.path.join(assets_dir, blend_file)
                if os.path.exists(fallback_path):
                    blend_path = fallback_path
                    search_location = "assets folder (fallback)"
                else:
                    show_popup(f"Body base file not found: {blend_file}\nSearched in: {search_location} and assets folder", icon='ERROR')
                    return {'CANCELLED'}
            else:
                show_popup(f"Body base file not found: {blend_file}\nSearched in: {search_location}", icon='ERROR')
                return {'CANCELLED'}
        
        print(f"Loading {blend_file} from {search_location}: {blend_path}")
        
        # Load the blend file
        try:
            with bpy.data.libraries.load(blend_path) as (data_from, data_to):
                # Debug: Print all available objects
                print(f"Available objects in {blend_file}: {list(data_from.objects)}")
                
                # Look for objects that match the expected naming pattern
                expected_object_name = f"{self.body_type}_{self.mesh_type}"
                target_objects = [name for name in data_from.objects if expected_object_name in name]
                
                # If no exact match, try loading all objects from the file
                if not target_objects:
                    print(f"No objects found with name containing '{expected_object_name}', loading all objects")
                    target_objects = data_from.objects
                
                data_to.objects = target_objects
                data_to.materials = data_from.materials
            
            # Add loaded objects to the scene
            loaded_objects = []
            for obj in data_to.objects:
                if obj is not None:
                    context.collection.objects.link(obj)
                    obj.select_set(True)
                    loaded_objects.append(obj)
            
            if loaded_objects:
                context.view_layer.objects.active = loaded_objects[0]
                body_type_name = dict(self.body_type_items)[self.body_type]
                mesh_type_name = dict(self.mesh_type_items)[self.mesh_type]
                show_popup(f"{body_type_name} {mesh_type_name} body base loaded successfully. Loaded {len(loaded_objects)} objects.")
            else:
                show_popup("No objects were loaded from the file.", icon='ERROR')
                return {'CANCELLED'}
            
            return {'FINISHED'}
            
        except Exception as e:
            self.display_popup_error(f"Error loading body base: {str(e)}")
            return {'CANCELLED'}
    
    @property
    def body_type_items(self):
        return [
            ('AM', 'Adult Male'),
            ('AF', 'Adult Female'),
            ('C', 'Child'),
            ('T', 'Toddler'),
            ('I', 'Infant'),
        ]
    
    @property
    def mesh_type_items(self):
        return [
            ('Full', 'Full Body'),
            ('Head', 'Head'),
            ('Top', 'Top'),
            ('Bottom', 'Bottom'),
            ('Feet', 'Feet'),
        ]
    

# Register and unregister functions
def register():
    bpy.utils.register_class(TSCT_OT_load_body_base)

def unregister():
    bpy.utils.unregister_class(TSCT_OT_load_body_base)