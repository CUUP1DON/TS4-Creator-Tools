import bpy
import os
from bpy.types import Operator

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
        
        # Construct the blend file path
        blend_file = f"{self.body_type}_{self.mesh_type}.blend"
        blend_path = os.path.join(assets_dir, blend_file)
        
        # Check if file exists
        if not os.path.exists(blend_path):
            self.display_popup_error(f"Body base file not found: {blend_file}")
            return {'CANCELLED'}
        
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
                self.display_popup_success(f"{body_type_name} {mesh_type_name} body base loaded successfully. Loaded {len(loaded_objects)} objects.")
            else:
                self.display_popup_error("No objects were loaded from the file.")
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
            ('Top', 'Top'),
            ('Bottom', 'Bottom'),
            ('Feet', 'Feet'),
        ]
    
    def display_popup_error(self, message):
        def popup(self, context):
            self.layout.label(text=message)
        bpy.context.window_manager.popup_menu(popup, title="Creator Tools", icon='ERROR')
    
    def display_popup_success(self, message):
        def popup(self, context):
            self.layout.label(text=message)
        bpy.context.window_manager.popup_menu(popup, title="Creator Tools", icon='INFO')

# Register and unregister functions
def register():
    bpy.utils.register_class(TSCT_OT_load_body_base)

def unregister():
    bpy.utils.unregister_class(TSCT_OT_load_body_base)