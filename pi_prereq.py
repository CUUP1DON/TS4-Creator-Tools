import bpy
from . import pi_errors

def reref(context):
    """Rename selected object to 'REF'"""
    # Get selected objects
    selected_objects = context.selected_objects
    # Check if exactly one object is selected
    if len(selected_objects) != 1:
        pi_errors.ErrorManager.show_error('no_object_selected',
            custom_message="Please select exactly one object",
            custom_details=[
                "Select the mesh you want to rename to 'REF'",
                "Only one object can be renamed at a time"
            ])
    else:
        # Get the selected object
        selected_object = selected_objects[0]
        # Rename the object
        selected_object.name = "REF"
        pi_errors.ErrorManager.show_success('operation_complete',
            custom_message=f"Object renamed to 'REF'",
            custom_details=["The selected object is now named 'REF'"])

def resfs(context):
    """Rename selected object to 's4studio_mesh_1'"""
    # Get selected objects
    selected_objects = context.selected_objects
    # Check if exactly one object is selected
    if len(selected_objects) != 1:
        pi_errors.ErrorManager.show_error('no_object_selected',
            custom_message="Please select exactly one object",
            custom_details=[
                "Select the mesh you want to rename to 's4studio_mesh_1'",
                "Only one object can be renamed at a time"
            ])
    else:
        # Get the selected object
        selected_object = selected_objects[0]
        # Rename the object
        selected_object.name = "s4studio_mesh_1"
        pi_errors.ErrorManager.show_success('operation_complete',
            custom_message=f"Object renamed to 's4studio_mesh_1'",
            custom_details=["The selected object is now named 's4studio_mesh_1'"])

class Reref(bpy.types.Operator):
    bl_idname = "object.reref"
    bl_label = "Rename Ref"
    bl_description = "Quickly renames your mesh to REF"
   
    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Rename REF")
        reref(context)  # Call the function directly since it's in the same file
        return {'FINISHED'}

class Resfs(bpy.types.Operator):
    bl_idname = "object.resfs"
    bl_label = "Rename SFS"
    bl_description = "Quickly renames your mesh to s4studio_mesh_1"
   
    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Rename S4S")
        resfs(context)  # Call the function directly since it's in the same file
        return {'FINISHED'}

def register():
    bpy.utils.register_class(Reref)
    bpy.utils.register_class(Resfs)

def unregister():
    bpy.utils.unregister_class(Reref)
    bpy.utils.unregister_class(Resfs)