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
no_mesh_selected = "Please select at least one mesh object"
already_linked = "Armature modifier already linked to a rig"
modifier_updated = "Existing armature modifier updated with new rig"
no_active_object = "No active object selected"
meshes_linked = "meshes successfully linked to rig"

# Shared function for linking mesh to rig
def link_mesh_to_rig(obj, target_rig):
    # Check if object already has an armature modifier
    armature_modifier = None
    for modifier in obj.modifiers:
        if modifier.type == 'ARMATURE':
            armature_modifier = modifier
            break
    
    # If armature modifier exists, update it with the new rig
    if armature_modifier is not None:
        if armature_modifier.object == target_rig:
            # Already linked to the same rig, no action needed
            return "already_linked"
        else:
            # Update to new rig (overwrite existing)
            armature_modifier.object = target_rig
            return "modifier_updated"
    
    # If no armature modifier exists, create one
    bpy.ops.object.modifier_add(type='ARMATURE')
    armature_modifier = obj.modifiers["Armature"]
    armature_modifier.object = target_rig
    
    return "linkrigsucc"


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
        
        # Get all selected objects and filter for mesh objects
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if not selected_objects:
            popups = [no_mesh_selected]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
            return {'CANCELLED'}
        
        # If multiple rigs found, invoke the rig selector
        if len(rig_objects) > 1:
            # Store the selected mesh objects for the rig selector to use
            context.scene.linkrig_target_meshes = ",".join([obj.name for obj in selected_objects])
            bpy.ops.object.select_rig('INVOKE_DEFAULT')
            return {'FINISHED'}
        
        # Use the first rig found if only one exists
        target_rig = rig_objects[0]
        
        # Link all selected meshes to the rig
        linked_count = 0
        for obj in selected_objects:
            # Set the object as active to ensure modifier operations work correctly
            context.view_layer.objects.active = obj
            result = link_mesh_to_rig(obj, target_rig)
            if result in ["linkrigsucc", "modifier_updated"]:
                linked_count += 1
        
        # Display appropriate success message
        if linked_count == 1:
            popups = [linkrigsucc]
        else:
            popups = [f"{linked_count} {meshes_linked}"]
        
        bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='INFO')
        return {'FINISHED'}


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
        # Get the target mesh objects
        target_mesh_names = getattr(context.scene, 'linkrig_target_meshes', "")
        if not target_mesh_names:
            self.display_popup_error("Target mesh objects not found")
            return {'CANCELLED'}
        
        mesh_names = target_mesh_names.split(",")
        target_meshes = []
        for name in mesh_names:
            if name in bpy.data.objects:
                target_meshes.append(bpy.data.objects[name])
        
        if not target_meshes:
            self.display_popup_error("No valid target mesh objects found")
            return {'CANCELLED'}
        
        # Get the selected rig
        if self.selected_rig not in bpy.data.objects:
            self.display_popup_error("Selected rig not found")
            return {'CANCELLED'}
        
        selected_rig_obj = bpy.data.objects[self.selected_rig]
        
        # Link all target meshes to the selected rig
        linked_count = 0
        for obj in target_meshes:
            # Set the object as active to ensure modifier operations work correctly
            context.view_layer.objects.active = obj
            result = link_mesh_to_rig(obj, selected_rig_obj)
            if result in ["linkrigsucc", "modifier_updated"]:
                linked_count += 1
        
        # Display appropriate success message
        if linked_count == 1:
            popups = [linkrigsucc]
        else:
            popups = [f"{linked_count} {meshes_linked}"]
        
        bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='INFO')
        
        # Clean up the stored mesh names
        context.scene.linkrig_target_meshes = ""
        
        return {'FINISHED'}
    
    def display_popup_error(self, message):
        def popup(self, context):
            self.layout.label(text=message)
        bpy.context.window_manager.popup_menu(popup, title="Creator Tools", icon='ERROR')


# Registration
def register():
    bpy.utils.register_class(linkrig)
    bpy.utils.register_class(TSCT_OT_select_rig)
    
    # Add properties to store the target mesh names
    bpy.types.Scene.linkrig_target_mesh = bpy.props.StringProperty()
    bpy.types.Scene.linkrig_target_meshes = bpy.props.StringProperty()


def unregister():
    bpy.utils.unregister_class(linkrig)
    bpy.utils.unregister_class(TSCT_OT_select_rig)
    
    # Remove the properties
    del bpy.types.Scene.linkrig_target_mesh
    del bpy.types.Scene.linkrig_target_meshes


if __name__ == "__main__":
    register()