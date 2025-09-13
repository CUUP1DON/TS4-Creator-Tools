import bpy
from . import pi_errors

def reref(context):  # Added context argument
    # Get selected objects
    selected_objects = context.selected_objects  # Use context to access selected_objects

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

class RefRename(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "reref.operator"
    bl_label = "Quickly renames your mesh."

    def execute(self, context):
        reref(context)  # Pass context argument
        return {'FINISHED'}

def register():
    bpy.utils.register_class(reref)

def unregister():
    bpy.utils.unregister_class(reref)
    
 
