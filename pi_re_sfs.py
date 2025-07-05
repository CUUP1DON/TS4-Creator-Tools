import bpy

def resfs(context):  # Added context argument
    # Get selected objects
    selected_objects = context.selected_objects  # Use context to access selected_objects

    # Check if exactly one object is selected
    if len(selected_objects) != 1:
        bpy.context.window_manager.popup_menu(lambda self, context: self.layout.label(text="Please select an object."), title="Creator Tools", icon='ERROR')
    else:
        # Get the selected object
        selected_object = selected_objects[0]

        # Rename the object
        selected_object.name = "s4studio_mesh_1"

class RefRename(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "resfs.operator"
    bl_label = "Quickly renames your mesh."

    def execute(self, context):
        resfs(context)  # Pass context argument
        return {'FINISHED'}

def register():
    bpy.utils.register_class(resfs)

def unregister():
    bpy.utils.unregister_class(resfs)
    
 
