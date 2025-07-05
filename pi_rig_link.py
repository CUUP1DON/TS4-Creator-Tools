import bpy

# Popup messages - you may need to adjust these based on your existing popup system
def display_popup_list(popups):
    def draw(self, context):
        for popup in popups:
            self.layout.label(text=popup)
    return draw

# Define popup messages (adjust these to match your existing ones)
norig = "No armature containing 'rig' found in scene"
linkrigsucc = "Mesh successfully linked to rig"
multirig = "Multiple rigs found. Please select which rig to use:"
no_mesh_selected = "Please select a mesh object"
already_linked = "Armature modifier already linked to a rig"
modifier_updated = "Existing armature modifier updated with new rig"
no_active_object = "No active object selected"

# Shared function for linking mesh to rig
def link_mesh_to_rig(obj, target_rig):
    # Check if object already has an armature modifier
    armature_modifier = None
    for modifier in obj.modifiers:
        if modifier.type == 'ARMATURE':
            armature_modifier = modifier
            break
    
    # If armature modifier exists, check if it's already linked to a rig
    if armature_modifier is not None:
        if armature_modifier.object is not None:
            # Check if the existing rig is different from the one we want to link
            if armature_modifier.object == target_rig:
                popups = [already_linked]
                bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='INFO')
                return {'FINISHED'}
            else:
                # Update to new rig
                armature_modifier.object = target_rig
                popups = [modifier_updated]
                bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='INFO')
                return {'FINISHED'}
        else:
            # Armature modifier exists but has no rig linked
            armature_modifier.object = target_rig
            popups = [linkrigsucc]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='INFO')
            return {'FINISHED'}
    
    # If no armature modifier exists, create one
    bpy.ops.object.modifier_add(type='ARMATURE')
    armature_modifier = obj.modifiers["Armature"]
    armature_modifier.object = target_rig
    
    popups = [linkrigsucc]
    bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='INFO')

    return {'FINISHED'}


# Link Rig
class linkrig(bpy.types.Operator):
    bl_idname = "object.linkrig"
    bl_label = "Link Rig"
    bl_description = "Link your mesh to the S4S Rig"

    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Link Rig")
        bpy.ops.object.mode_set(mode='OBJECT')

        # Find all armatures containing 'rig' in their name
        rig_objects = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE' and 'rig' in obj.name.lower()]
        
        if not rig_objects:
            popups = [norig]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
            return {'CANCELLED'}
        
        # Get the active object
        obj = context.active_object
        if not obj:
            popups = [no_active_object]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
            return {'CANCELLED'}
        
        if obj.type != 'MESH':
            popups = [no_mesh_selected]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
            return {'CANCELLED'}
        
        # If multiple rigs found, invoke the rig selector
        if len(rig_objects) > 1:
            # Store the mesh object for the rig selector to use
            context.scene.linkrig_target_mesh = obj.name
            bpy.ops.object.select_rig('INVOKE_DEFAULT')
            return {'FINISHED'}
        
        # Use the first rig found if only one exists
        target_rig = rig_objects[0]
        
        # Link the mesh to the rig
        result = link_mesh_to_rig(obj, target_rig)
        return result


# Rig Selector Operator
class TSCT_OT_select_rig(bpy.types.Operator):
    bl_idname = "object.select_rig"
    bl_label = "Select Rig"
    bl_description = "Select which rig to link to the mesh"
    bl_options = {'REGISTER', 'UNDO'}
    
    def get_rig_items(self, context):
        # Find all armatures containing 'rig' in their name
        rig_objects = [obj for obj in bpy.data.objects if obj.type == 'ARMATURE' and 'rig' in obj.name.lower()]
        items = []
        for i, rig in enumerate(rig_objects):
            items.append((rig.name, rig.name, f"Select {rig.name}"))
        return items
    
    selected_rig: bpy.props.EnumProperty(
        name="Available Rigs",
        description="Choose which rig to link to your mesh",
        items=get_rig_items
    )
    
    def invoke(self, context, event):
        # Force the dialog to appear
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        # Get the target mesh object
        target_mesh_name = getattr(context.scene, 'linkrig_target_mesh', None)
        if not target_mesh_name or target_mesh_name not in bpy.data.objects:
            self.display_popup_error("Target mesh object not found")
            return {'CANCELLED'}
        
        target_mesh = bpy.data.objects[target_mesh_name]
        
        # Get the selected rig
        if self.selected_rig not in bpy.data.objects:
            self.display_popup_error("Selected rig not found")
            return {'CANCELLED'}
        
        selected_rig_obj = bpy.data.objects[self.selected_rig]
        
        # Use the shared linking logic
        result = link_mesh_to_rig(target_mesh, selected_rig_obj)
        
        # Clean up the stored mesh name
        context.scene.linkrig_target_mesh = ""
        
        return result
    
    def display_popup_error(self, message):
        def popup(self, context):
            self.layout.label(text=message)
        bpy.context.window_manager.popup_menu(popup, title="Creator Tools", icon='ERROR')


# Registration
def register():
    bpy.utils.register_class(linkrig)
    bpy.utils.register_class(TSCT_OT_select_rig)
    
    # Add a property to store the target mesh name
    bpy.types.Scene.linkrig_target_mesh = bpy.props.StringProperty()


def unregister():
    bpy.utils.unregister_class(linkrig)
    bpy.utils.unregister_class(TSCT_OT_select_rig)
    
    # Remove the property
    del bpy.types.Scene.linkrig_target_mesh


if __name__ == "__main__":
    register()