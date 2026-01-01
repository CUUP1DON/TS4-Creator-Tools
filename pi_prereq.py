import bpy
import re
from . import pi_errors

def reref(context):
    """Rename selected objects to 'REF_1', 'REF_2', etc."""
    # Get selected objects
    selected_objects = context.selected_objects
    # Check if any objects are selected
    if not selected_objects:
        pi_errors.ErrorManager.show_error('no_object_selected',
            custom_message="Please select at least one object",
            custom_details=[
                "Select the mesh(es) you want to rename to 'REF_1', 'REF_2', etc.",
                "Multiple objects can be renamed at once"
            ])
        return

    # Get existing names
    existing_names = set(obj.name for obj in bpy.data.objects)

    # Rename the objects
    renamed_names = []
    for i, selected_object in enumerate(selected_objects):
        new_name = f"REF_{i + 1}"
        while new_name in existing_names:
            match = re.search(r'(\d+)$', new_name)
            if match:
                num = int(match.group(1)) + 1
                new_name = re.sub(r'\d+$', str(num), new_name)
            else:
                new_name += "_1"
        selected_object.name = new_name
        existing_names.add(new_name)
        renamed_names.append(new_name)

    # Success message
    message = f"{len(selected_objects)} object{'s' if len(selected_objects) > 1 else ''} renamed"
    details = [f"Renamed to: {', '.join(renamed_names)}"]
    pi_errors.ErrorManager.show_success('operation_complete',
        custom_message=message,
        custom_details=details)

def resfs(context):
    """Rename selected objects to 's4studio_mesh_1', 's4studio_mesh_2', etc."""
    # Get selected objects
    selected_objects = context.selected_objects
    # Check if any objects are selected
    if not selected_objects:
        pi_errors.ErrorManager.show_error('no_object_selected',
            custom_message="Please select at least one object",
            custom_details=[
                "Select the mesh(es) you want to rename to 's4studio_mesh_1', 's4studio_mesh_2', etc.",
                "Multiple objects can be renamed at once"
            ])
        return

    # Get existing names
    existing_names = set(obj.name for obj in bpy.data.objects)

    # Rename the objects
    renamed_names = []
    for i, selected_object in enumerate(selected_objects):
        new_name = f"s4studio_mesh_{i + 1}"
        while new_name in existing_names:
            match = re.search(r'(\d+)$', new_name)
            if match:
                num = int(match.group(1)) + 1
                new_name = re.sub(r'\d+$', str(num), new_name)
            else:
                new_name += "_1"
        selected_object.name = new_name
        existing_names.add(new_name)
        renamed_names.append(new_name)

    # Success message
    message = f"{len(selected_objects)} object{'s' if len(selected_objects) > 1 else ''} renamed"
    details = [f"Renamed to: {', '.join(renamed_names)}"]
    pi_errors.ErrorManager.show_success('operation_complete',
        custom_message=message,
        custom_details=details)

class Reref(bpy.types.Operator):
    bl_idname = "object.reref"
    bl_label = "Rename Ref"
    bl_description = "Quickly renames selected meshes to REF_1, REF_2, etc."
   
    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Rename REF")
        reref(context)  # Call the function directly since it's in the same file
        return {'FINISHED'}

class Resfs(bpy.types.Operator):
    bl_idname = "object.resfs"
    bl_label = "Rename SFS"
    bl_description = "Quickly renames selected meshes to s4studio_mesh_1, s4studio_mesh_2, etc."
   
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