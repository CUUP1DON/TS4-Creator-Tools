# Validate animation choice for adults
import bpy
import os
from bpy.types import Operator
from .ci_asset_management import show_popup

class TSCT_OT_load_anim(Operator):
    bl_idname = "object.load_anim"
    bl_label = "Load an Animation"
    bl_description = "Load an Animation"
    bl_options = {'REGISTER', 'UNDO'}
    
    def update_body_type(self, context):
        """Called when body type changes"""
        pass  # No longer need to restrict range of motion for adults

    body_type: bpy.props.EnumProperty(
        name="Body Type",
        description="Body type for animation",
        items=[
            ('AM', 'Adult Male', 'Adult Male body type'),
            ('AF', 'Adult Female', 'Adult Female body type'),
            ('C', 'Child', 'Child body type'),
            ('T', 'Toddler', 'Toddler body type'),
            ('I', 'Infant', 'Infant body type'),
        ],
        default='AM',
        update=update_body_type
    )
    

    def update_animation(self, context):
        """Called when animation changes"""
        pass  # No longer need to restrict range of motion for adults

    animation: bpy.props.EnumProperty(
        name="Animation",
        description="Animation to load for testing",
        items=[
            ('walk', 'Walk', 'Walking animation'),
            ('chair', 'Chair', 'Chair sit/stand animation'),
            ('rangeofmotion', 'Range of Motion', 'Range of motion animation'),
            ('fairy_fly', 'Fairy Fly', 'Fairy flying animation for wings'),
            ('mermaid_swim', 'Mermaid Swim', 'Mermaid swimming animation'),
        ],
        default='walk',
        update=update_animation
    )
    
    def invoke(self, context, event):
        # Force the dialog to appear
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "body_type")
        layout.prop(self, "animation")
    
    def get_body_type_name(self, body_type_code):
        """Get the display name for a body type code"""
        body_type_names = {
            'AM': 'Adult Male',
            'AF': 'Adult Female',
            'C': 'Child',
            'T': 'Toddler',
            'I': 'Infant'
        }
        return body_type_names.get(body_type_code, body_type_code)
    
    def get_animation_name(self, animation_code):
        """Get the display name for an animation code"""
        animation_names = {
            'walk': 'Walk',
            'chair': 'Chair',
            'rangeofmotion': 'Range of Motion',
            'fairy_fly': 'Fairy Fly',
            'mermaid_swim': 'Mermaid Swim'
        }
        return animation_names.get(animation_code, animation_code)
    
    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Load Animation")
        
        # Find armature - check active object first, then search scene
        armature_obj = None
        
        # Check if active object is an armature
        if context.active_object and context.active_object.type == 'ARMATURE':
            armature_obj = context.active_object
        else:
            # If active object is a mesh with armature parent/modifier, use that
            obj = context.active_object
            if obj and obj.type == 'MESH':
                if obj.parent and obj.parent.type == 'ARMATURE':
                    armature_obj = obj.parent
                else:
                    for modifier in obj.modifiers:
                        if modifier.type == 'ARMATURE' and modifier.object:
                            armature_obj = modifier.object
                            break
            
            # If still no armature found, search for any armature in the scene
            if not armature_obj:
                for obj in context.scene.objects:
                    if obj.type == 'ARMATURE':
                        armature_obj = obj
                        break
        
        if not armature_obj:
            show_popup("No armature found in scene")
            return {'CANCELLED'}
        
        # Store original state before applying test animation
        self.store_original_state(context, armature_obj)
        
        # Get the addon directory and construct animation path
        addon_dir = os.path.dirname(os.path.realpath(__file__))
        assets_dir = os.path.join(addon_dir, "assets")
        animations_dir = os.path.join(assets_dir, "anim")
        
        # Construct the blend file name
        blend_file = self.get_blend_filename()
        blend_path = os.path.join(animations_dir, blend_file)
        
        # Check if file exists
        if not os.path.exists(blend_path):
            # Try assets folder as fallback
            fallback_path = os.path.join(assets_dir, blend_file)
            if os.path.exists(fallback_path):
                blend_path = fallback_path
            else:
                show_popup(f"Animation file not found: {blend_file}")
                return {'CANCELLED'}
        
        print(f"Loading animation {blend_file}: {blend_path}")
        
        # Load the animation
        try:
            with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
                print(f"Available actions in {blend_file}: {list(data_from.actions)}")

                # Look for the expected action name
                expected_action_name = self.get_expected_action_name()
                target_actions = [name for name in data_from.actions if expected_action_name in name.lower()]

                # If no exact match, try loading the first action
                if not target_actions and data_from.actions:
                    print(f"No action found with name containing '{expected_action_name}', using first available")
                    target_actions = [data_from.actions[0]]

                if not target_actions:
                    show_popup("No actions found in animation file")
                    return {'CANCELLED'}

                data_to.actions = target_actions
            
            # Apply the loaded action to the armature
            if data_to.actions:
                test_action = data_to.actions[0]

                # Ensure armature is active in the view layer (Blender 4.x requirement)
                original_active = context.active_object
                context.view_layer.objects.active = armature_obj

                # Ensure animation data exists
                if not armature_obj.animation_data:
                    armature_obj.animation_data_create()

                # Handle Action Slots for Blender 4.x compatibility
                anim_data = armature_obj.animation_data
                anim_data.action = test_action

                # Try action slot assignment (Blender 4.x+)
                try:
                    # Use action_suitable_slots to get an appropriate slot (per Blender docs)
                    if hasattr(anim_data, 'action_suitable_slots') and anim_data.action_suitable_slots:
                        anim_data.action_slot = anim_data.action_suitable_slots[0]
                    # Fallback: manually get the first slot (for Legacy Slots)
                    elif hasattr(test_action, 'slots') and test_action.slots:
                        anim_data.action_slot = test_action.slots[0]
                except Exception:
                    # If action slot assignment fails, fall back to legacy method
                    pass

                # Force update to ensure the action is properly applied
                bpy.context.view_layer.update()

                # Verify the action was applied
                if hasattr(armature_obj.animation_data, 'action_slots'):
                    if armature_obj.animation_data.action_slot and armature_obj.animation_data.action_slot.action == test_action:
                        print(f"✓ Action successfully applied to action slot on {armature_obj.name}")
                    else:
                        print(f"✗ Failed to apply action to action slot on {armature_obj.name}")
                else:
                    if armature_obj.animation_data.action == test_action:
                        print(f"✓ Action successfully applied to {armature_obj.name}")
                    else:
                        print(f"✗ Failed to apply action to {armature_obj.name}")

                # Restore original active object if needed
                if original_active and original_active != armature_obj:
                    context.view_layer.objects.active = original_active
                
                # Adjust timeline to match animation length
                if test_action.frame_range:
                    start_frame = int(test_action.frame_range[0])
                    end_frame = int(test_action.frame_range[1])
                    
                    # Store original timeline settings
                    context.scene['tsct_original_frame_start'] = context.scene.frame_start
                    context.scene['tsct_original_frame_end'] = context.scene.frame_end
                    
                    # Set new timeline range
                    context.scene.frame_start = start_frame
                    context.scene.frame_end = end_frame
                    
                    print(f"Timeline adjusted: frames {start_frame} to {end_frame}")
                else:
                    print("Warning: Action has no frame range data")
                
                # Set frame to beginning
                context.scene.frame_set(context.scene.frame_start)
                
                # Store test state info
                context.scene['tsct_testing_weights'] = True
                context.scene['tsct_test_action'] = test_action
                
                body_type_name = self.get_body_type_name(self.body_type)
                animation_name = self.get_animation_name(self.animation)
                show_popup(f"{animation_name} loaded on '{armature_obj.name}'.")
                
                return {'FINISHED'}
            else:
                show_popup("Failed to load animation action")
                return {'CANCELLED'}
                
        except Exception as e:
            show_popup(f"Error loading animation: {str(e)}")
            return {'CANCELLED'}
    
    def store_original_state(self, context, armature_obj):
        """Store the original animation state"""
        if armature_obj.animation_data and armature_obj.animation_data.action:
            context.scene['tsct_original_action'] = armature_obj.animation_data.action
        else:
            context.scene['tsct_original_action'] = None
        context.scene['tsct_original_frame'] = context.scene.frame_current
        # Store original timeline range
        context.scene['tsct_original_frame_start'] = context.scene.frame_start
        context.scene['tsct_original_frame_end'] = context.scene.frame_end
        context.scene['tsct_testing_weights'] = False
    
    def get_blend_filename(self):
        """Generate the blend file name based on body type and animation"""
        # Special case: chair animations for adults use generic "a_chair"
        if self.animation == 'chair' and self.body_type in ['AM', 'AF']:
            return "a_chair.blend"
        # Special case: range of motion for adults uses child blend file
        elif self.animation == 'rangeofmotion' and self.body_type in ['AM', 'AF']:
            return "c_rangeofmotion.blend"
        # Special case: fairy fly animation uses generic "fairy_fly" for all body types
        elif self.animation == 'fairy_fly':
            return "fairy_fly.blend"
        # Special case: mermaid swim animation uses generic "mermaid_swim" for all body types
        elif self.animation == 'mermaid_swim':
            return "mermaid_swim.blend"
        return f"{self.body_type.lower()}_{self.animation}.blend"
    
    def get_expected_action_name(self):
        """Generate the expected action name"""
        # Special case: chair animations for adults use generic "a_chair" action name
        if self.animation == 'chair' and self.body_type in ['AM', 'AF']:
            return "a_chair"
        # Special case: range of motion for adults uses child action name
        elif self.animation == 'rangeofmotion' and self.body_type in ['AM', 'AF']:
            return "c_rangeofmotion"
        # Special case: fairy fly animation uses generic "fairy_fly" for all body types
        elif self.animation == 'fairy_fly':
            return "fairy_fly"
        # Special case: mermaid swim animation uses generic "mermaid_swim" for all body types
        elif self.animation == 'mermaid_swim':
            return "mermaid_swim"
        return f"{self.body_type.lower()}_{self.animation}".lower()
    
    @property
    def body_type_items(self):
        return [
            ('AM', 'Adult Male'),
            ('AF', 'Adult Female'),
            ('C', 'Child'),
            ('T', 'Toddler'),
            ('I', 'Infant'),
        ]
    


class TSCT_OT_restore_anim(Operator):
    bl_idname = "object.restore_anim"
    bl_label = "Restore Rest Pose"
    bl_description = "Restore the original animation"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Restore Original Animation")
        
        # Find armature - check active object first, then search scene
        armature_obj = None
        
        # Check if active object is an armature
        if context.active_object and context.active_object.type == 'ARMATURE':
            armature_obj = context.active_object
        else:
            # If active object is a mesh with armature parent/modifier, use that
            obj = context.active_object
            if obj and obj.type == 'MESH':
                if obj.parent and obj.parent.type == 'ARMATURE':
                    armature_obj = obj.parent
                else:
                    for modifier in obj.modifiers:
                        if modifier.type == 'ARMATURE' and modifier.object:
                            armature_obj = modifier.object
                            break
            
            # If still no armature found, search for any armature in the scene
            if not armature_obj:
                for obj in context.scene.objects:
                    if obj.type == 'ARMATURE':
                        armature_obj = obj
                        break
        
        if not armature_obj:
            show_popup("No armature found in scene")
            return {'CANCELLED'}
        
        # Check if we're in testing mode
        if not context.scene.get('tsct_testing_weights', False):
            show_popup("No animations to be cleared.")
            return {'CANCELLED'}
        
        try:
            # Switch to pose mode and select all bones to clear transforms
            original_mode = context.object.mode if context.object else 'OBJECT'
            original_active = context.active_object
            
            # Set armature as active and switch to pose mode
            context.view_layer.objects.active = armature_obj
            bpy.ops.object.mode_set(mode='POSE')

            # Clear transforms for ALL bones (including hidden ones)
            # Direct bone manipulation bypasses visibility restrictions
            for bone in armature_obj.pose.bones:
                bone.location = (0.0, 0.0, 0.0)
                bone.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
                bone.rotation_euler = (0.0, 0.0, 0.0)
                bone.scale = (1.0, 1.0, 1.0)
            
            # Remove the action completely
            if armature_obj.animation_data:
                armature_obj.animation_data.action = None
            
            # Clean up test action (removes it from blend file)
            if 'tsct_test_action' in context.scene:
                test_action = context.scene['tsct_test_action']
                if test_action and test_action.users == 0:
                    bpy.data.actions.remove(test_action)
            
            # Restore original frame
            if 'tsct_original_frame' in context.scene:
                context.scene.frame_set(context.scene['tsct_original_frame'])
            
            # Restore original timeline range
            if 'tsct_original_frame_start' in context.scene:
                context.scene.frame_start = context.scene['tsct_original_frame_start']
            if 'tsct_original_frame_end' in context.scene:
                context.scene.frame_end = context.scene['tsct_original_frame_end']
            
            # Restore original mode and active object
            bpy.ops.object.mode_set(mode='OBJECT')
            if original_active:
                context.view_layer.objects.active = original_active
                if original_mode != 'OBJECT':
                    bpy.ops.object.mode_set(mode=original_mode)
            
            # Clear testing state
            context.scene['tsct_testing_weights'] = False
            if 'tsct_original_action' in context.scene:
                del context.scene['tsct_original_action']
            if 'tsct_original_frame' in context.scene:
                del context.scene['tsct_original_frame']
            if 'tsct_original_frame_start' in context.scene:
                del context.scene['tsct_original_frame_start']
            if 'tsct_original_frame_end' in context.scene:
                del context.scene['tsct_original_frame_end']
            if 'tsct_test_action' in context.scene:
                del context.scene['tsct_test_action']
            
            show_popup(f"Animation removed from '{armature_obj.name}' and all pose transforms cleared")
            return {'FINISHED'}
            
        except Exception as e:
            show_popup(f"Error restoring animation: {str(e)}")
            return {'CANCELLED'}
    


# Register and unregister functions
def register():
    bpy.utils.register_class(TSCT_OT_load_anim)
    bpy.utils.register_class(TSCT_OT_restore_anim)

def unregister():
    bpy.utils.unregister_class(TSCT_OT_load_anim)
    bpy.utils.unregister_class(TSCT_OT_restore_anim)