import bpy
import os
from bpy.types import Operator
from bpy.props import EnumProperty
from .ci_asset_management import (
    get_custom_assets_path, 
    get_asset_items, 
    show_popup,
    get_available_rigs,
    get_rig_items
)

class TSCT_OT_load_custom_anim(Operator):
    """Load custom animation"""
    bl_idname = "tsct.load_custom_anim"
    bl_label = "Load Custom Animation"
    bl_description = "Load a custom animation and apply it to a selected rig"
    bl_options = {'REGISTER', 'UNDO'}
    
    def get_anim_items(self, context):
        return get_asset_items("Anim")
    
    anim_item: EnumProperty(
        name="Custom Animation", 
        description="Select a custom animation to load", 
        items=get_anim_items
    )
    
    target_rig: EnumProperty(
        name="Target Rig",
        description="Select the rig to apply the animation to",
        items=get_rig_items
    )
    
    def invoke(self, context, event):
        # Check if we have any animations first
        anim_items = get_asset_items("Anim")
        if len(anim_items) == 1 and anim_items[0][0] == 'NONE':
            show_popup("No custom animations found.", icon='ERROR')
            return {'CANCELLED'}
        
        # Check if we have any rigs
        rigs = get_available_rigs(context)
        if not rigs:
            show_popup("No rigs in scene.", icon='ERROR')
            return {'CANCELLED'}
        
        # If only one rig, select it automatically
        if len(rigs) == 1:
            self.target_rig = rigs[0].name
        
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        
        # Animation selection
        layout.prop(self, "anim_item")
        
        # Rig selection (only show if more than one rig available)
        rigs = get_available_rigs(context)
        if len(rigs) > 1:
            layout.separator()
            layout.prop(self, "target_rig")
        elif len(rigs) == 1:
            # Show selected rig as info
            layout.separator()
            box = layout.box()
            box.label(text=f"Target Rig: {rigs[0].name}", icon='ARMATURE_DATA')

    def execute(self, context):
        if self.anim_item == 'NONE':
            return {'CANCELLED'}
        
        if self.target_rig == 'NONE':
            show_popup("No rig selected. Please select a target rig.", icon='ERROR')
            return {'CANCELLED'}
        
        bpy.ops.ed.undo_push(message="Creator Tools: Load Custom Animation")
        
        file_path = os.path.join(get_custom_assets_path(), "Anim", self.anim_item)
        
        if not os.path.exists(file_path):
            show_popup(f"File not found: {self.anim_item}", icon='ERROR')
            return {'CANCELLED'}
        
        return self.load_animation_file(context, file_path, os.path.basename(file_path)[:-6])

    def load_animation_file(self, context, blend_path, asset_name):
        """Load animation file - only import actions, don't import objects/meshes"""
        try:
            # Get the selected rig
            armature_obj = None
            if hasattr(self, 'target_rig') and self.target_rig != 'NONE':
                armature_obj = bpy.data.objects.get(self.target_rig)
            
            if not armature_obj or armature_obj.type != 'ARMATURE':
                show_popup("No valid armature selected. Please select a rig to apply the animation to.", icon='ERROR')
                return {'CANCELLED'}
            
            # Store original state before applying animation
            self.store_original_state(context, armature_obj)
            
            # Load only the actions from the animation file
            loaded_actions = []
            with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
                print(f"Available actions in {os.path.basename(blend_path)}: {list(data_from.actions)}")
                
                if not data_from.actions:
                    show_popup("No actions found in animation file.", icon='ERROR')
                    return {'CANCELLED'}
                
                # Load all actions
                data_to.actions = data_from.actions
            
            # Process loaded actions
            if data_to.actions:
                loaded_actions = [action for action in data_to.actions if action is not None]
                
                if loaded_actions:
                    # Apply the first action to the selected armature
                    first_action = loaded_actions[0]

                    # Ensure armature is active in the view layer (Blender 4.x requirement)
                    original_active = context.active_object
                    context.view_layer.objects.active = armature_obj

                    # Ensure animation data exists
                    if not armature_obj.animation_data:
                        armature_obj.animation_data_create()

                    # Handle Action Slots for Blender 4.x compatibility
                    anim_data = armature_obj.animation_data
                    anim_data.action = first_action

                    # Try action slot assignment (Blender 4.x+)
                    try:
                        # Use action_suitable_slots to get an appropriate slot (per Blender docs)
                        if hasattr(anim_data, 'action_suitable_slots') and anim_data.action_suitable_slots:
                            anim_data.action_slot = anim_data.action_suitable_slots[0]
                        # Fallback: manually get the first slot (for Legacy Slots)
                        elif hasattr(first_action, 'slots') and first_action.slots:
                            anim_data.action_slot = first_action.slots[0]
                    except Exception:
                        # If action slot assignment fails, fall back to legacy method
                        pass

                    # Force update to ensure the action is properly applied
                    bpy.context.view_layer.update()

                    # Verify the action was applied
                    if hasattr(armature_obj.animation_data, 'action_slots'):
                        if armature_obj.animation_data.action_slot and armature_obj.animation_data.action_slot.action == first_action:
                            print(f"✓ Action successfully applied to action slot on {armature_obj.name}")
                        else:
                            print(f"✗ Failed to apply action to action slot on {armature_obj.name}")
                    else:
                        if armature_obj.animation_data.action == first_action:
                            print(f"✓ Action successfully applied to {armature_obj.name}")
                        else:
                            print(f"✗ Failed to apply action to {armature_obj.name}")

                    # Restore original active object if needed
                    if original_active and original_active != armature_obj:
                        context.view_layer.objects.active = original_active
                    
                    # Adjust timeline to match animation length
                    if first_action.frame_range:
                        start_frame = int(first_action.frame_range[0])
                        end_frame = int(first_action.frame_range[1])
                        
                        context.scene.frame_start = start_frame
                        context.scene.frame_end = end_frame
                        context.scene.frame_set(start_frame)
                        
                        print(f"Timeline adjusted: frames {start_frame} to {end_frame}")
                    else:
                        print("Warning: Action has no frame range data")
                    
                    # Mark as testing mode
                    context.scene['tsct_testing_weights'] = True
                    context.scene['tsct_test_action'] = first_action
                    
                    success_msg = f"Loaded {len(loaded_actions)} action(s)."
                    show_popup(success_msg)
                    return {'FINISHED'}
            
            show_popup("No valid actions were loaded from the file.", icon='ERROR')
            return {'CANCELLED'}
            
        except Exception as e:
            show_popup(f"Error loading Custom Animation: {str(e)}", icon='ERROR')
            print(f"Full error details: {e}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}

    def store_original_state(self, context, armature_obj):
        """Store the original animation state"""
        if armature_obj.animation_data and armature_obj.animation_data.action:
            context.scene['tsct_original_action'] = armature_obj.animation_data.action
        else:
            context.scene['tsct_original_action'] = None
        context.scene['tsct_original_frame'] = context.scene.frame_current
        # Store original timeline range - this is the key addition
        context.scene['tsct_original_frame_start'] = context.scene.frame_start
        context.scene['tsct_original_frame_end'] = context.scene.frame_end

# Registration
classes = [
    TSCT_OT_load_custom_anim,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)