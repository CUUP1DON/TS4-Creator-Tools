import bpy
import os
from bpy.types import Operator

class TSCT_OT_load_rig(Operator):
    bl_idname = "object.load_rig"
    bl_label = "Load Rig"
    bl_description = "Load a rig armature"
    bl_options = {'REGISTER', 'UNDO'}
    
    rig_type: bpy.props.EnumProperty(
        name="Rig Type",
        description="Type of rig to load",
        items=[
            ('AM', 'Adult Male', 'Adult Male rig'),
            ('AF', 'Adult Female', 'Adult Female rig'),
            ('C', 'Child', 'Child rig'),
            ('T', 'Toddler', 'Toddler rig'),
            ('I', 'Infant', 'Infant rig'),
        ],
        default='AM'
    )
    
    def invoke(self, context, event):
        # Force the dialog to appear
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Load Rig")
        
        # Get the addon directory
        addon_dir = os.path.dirname(os.path.realpath(__file__))
        assets_dir = os.path.join(addon_dir, "assets")
        
        # Construct the blend file path
        blend_file = f"{self.rig_type}_Rig.blend"
        blend_path = os.path.join(assets_dir, blend_file)
        
        # Check if file exists
        if not os.path.exists(blend_path):
            self.display_popup_error(f"Rig file not found: {blend_file}")
            return {'CANCELLED'}
        
        # Load the blend file
        try:
            with bpy.data.libraries.load(blend_path) as (data_from, data_to):
                # Debug: Print all available objects and armatures
                print(f"Available objects in {blend_file}: {list(data_from.objects)}")
                print(f"Available armatures in {blend_file}: {list(data_from.armatures)}")
                
                # Look for armature objects that match the expected naming pattern
                expected_rig_name = f"{self.rig_type}_Rig"
                target_objects = [name for name in data_from.objects if expected_rig_name in name or "rig" in name.lower()]
                
                # If no exact match, try loading all armature objects from the file
                if not target_objects:
                    print(f"No objects found with name containing '{expected_rig_name}', loading all objects")
                    target_objects = data_from.objects
                
                data_to.objects = target_objects
                data_to.armatures = data_from.armatures
                data_to.materials = data_from.materials
            
            # Add loaded objects to the scene
            loaded_objects = []
            loaded_armatures = []
            
            for obj in data_to.objects:
                if obj is not None:
                    context.collection.objects.link(obj)
                    obj.select_set(True)
                    loaded_objects.append(obj)
                    
                    # Check if it's an armature
                    if obj.type == 'ARMATURE':
                        loaded_armatures.append(obj)
            
            if loaded_objects:
                # Set the first armature as active if available, otherwise the first object
                if loaded_armatures:
                    context.view_layer.objects.active = loaded_armatures[0]
                else:
                    context.view_layer.objects.active = loaded_objects[0]
                
                rig_type_name = dict(self.rig_type_items)[self.rig_type]
                if loaded_armatures:
                    self.display_popup_success(f"{rig_type_name} rig loaded successfully. Loaded {len(loaded_armatures)} armature(s) and {len(loaded_objects)} total objects.")
                else:
                    self.display_popup_success(f"{rig_type_name} rig loaded successfully. Loaded {len(loaded_objects)} objects (no armatures detected).")
            else:
                self.display_popup_error("No objects were loaded from the file.")
                return {'CANCELLED'}
            
            return {'FINISHED'}
            
        except Exception as e:
            self.display_popup_error(f"Error loading rig: {str(e)}")
            return {'CANCELLED'}
    
    @property
    def rig_type_items(self):
        return [
            ('AM', 'Adult Male'),
            ('AF', 'Adult Female'),
            ('C', 'Child'),
            ('T', 'Toddler'),
            ('I', 'Infant'),
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
    bpy.utils.register_class(TSCT_OT_load_rig)

def unregister():
    bpy.utils.unregister_class(TSCT_OT_load_rig)