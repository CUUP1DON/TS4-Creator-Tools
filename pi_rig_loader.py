import bpy
import os
from bpy.types import Operator
from .ci_asset_management import show_popup

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
            ('F_Mermaid', 'Female Mermaid', 'Female Mermaid rig'),
            ('M_Merman', 'Male Merman', 'Male Merman rig'),
            ('M_Werewolf', 'Male Werewolf', 'Male Werewolf rig'),
            ('F_Werewolf', 'Female Werewolf', 'Female Werewolf rig'),
            ('M_Fairy', 'Male Fairy', 'Male Fairy rig'),
            ('F_Fairy', 'Female Fairy', 'Female Fairy rig'),
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
        rig_dir = os.path.join(assets_dir, "rig")

        # Construct the blend file path
        blend_file = f"{self.rig_type}_Rig.blend"
        blend_path = os.path.join(rig_dir, blend_file)
        
        # Check if file exists
        if not os.path.exists(blend_path):
            show_popup(f"Rig file not found: {blend_file}", icon='ERROR')
            return {'CANCELLED'}
        
        # Load the blend file
        try:
            with bpy.data.libraries.load(blend_path) as (data_from, data_to):
                # Debug: Print all available objects and armatures
                print(f"Available objects in {blend_file}: {list(data_from.objects)}")
                print(f"Available armatures in {blend_file}: {list(data_from.armatures)}")
                
                # Filter to only load armature objects
                armature_objects = [name for name in data_from.objects 
                                  if any(obj_name == name for obj_name in data_from.objects) 
                                  and name in [obj.name for obj in bpy.data.objects.values() 
                                              if obj.type == 'ARMATURE'] 
                                  or 'rig' in name.lower() or 'armature' in name.lower()]
                
                # If the filtering above is complex, let's simplify by just loading objects 
                # and filtering them after based on type
                data_to.objects = data_from.objects
                data_to.armatures = data_from.armatures if data_from.armatures else []
            
            # Add only armature objects to the scene
            loaded_armatures = []
            
            for obj in data_to.objects:
                if obj is not None and obj.type == 'ARMATURE':
                    context.collection.objects.link(obj)
                    obj.select_set(True)
                    loaded_armatures.append(obj)
                    print(f"Loaded armature: {obj.name}")
            
            if loaded_armatures:
                # Select all loaded armatures
                for obj in loaded_armatures:
                    obj.select_set(True)
                # Set the first armature as active
                context.view_layer.objects.active = loaded_armatures[0]
                
                rig_type_name = dict(self.rig_type_items)[self.rig_type]
                show_popup(f"{rig_type_name} rig loaded successfully. Loaded {len(loaded_armatures)} armature(s).")
                return {'FINISHED'}
            else:
                show_popup("No armatures found in the rig file.", icon='ERROR')
                return {'CANCELLED'}

        except Exception as e:
            show_popup(f"Error loading rig: {str(e)}", icon='ERROR')
            print(f"Full error details: {e}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}
    
    @property
    def rig_type_items(self):
        return [
            ('AM', 'Adult Male'),
            ('AF', 'Adult Female'),
            ('C', 'Child'),
            ('T', 'Toddler'),
            ('I', 'Infant'),
            ('F_Mermaid', 'Female Mermaid'),
            ('M_Merman', 'Male Merman'),
            ('M_Werewolf', 'Male Werewolf'),
            ('F_Werewolf', 'Female Werewolf'),
            ('M_Fairy', 'Male Fairy'),
            ('F_Fairy', 'Female Fairy'),
        ]
    

# Register and unregister functions
def register():
    bpy.utils.register_class(TSCT_OT_load_rig)

def unregister():
    bpy.utils.unregister_class(TSCT_OT_load_rig)