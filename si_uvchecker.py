import bpy

# UV Checker Operator
class si_uvchecker(bpy.types.Operator):
    bl_idname = "object.si_uvchecker"
    bl_label = "UV Checker"
    bl_description = "Checks your uv maps. Adds & renames them as needed"
    
    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: UV Checker")
       
        bpy.ops.object.mode_set(mode='OBJECT')
        obj = context.view_layer.objects.active
       
        if obj is None:
            self.report({'ERROR'}, "Please select or unhide your object.")
            return {'CANCELLED'}
        
        # Switch to edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        
        # UV maps logic
        uv_0_exists = False
        uv_1_exists = False
        renamed_uv_map = False
        maps_already_exist = False
        
        popup_messages = []
        
        # Check for existing uv_1 and remove duplicates
        uv_1_maps = [uv for uv in obj.data.uv_layers if uv.name.startswith("uv_1")]
        if len(uv_1_maps) > 1:
            # Keep only the first uv_1 and remove the rest
            for i, uv_map in enumerate(uv_1_maps):
                if i == 0:
                    uv_map.name = "uv_1"  # Ensure the first one is named exactly "uv_1"
                    uv_1_exists = True
                else:
                    obj.data.uv_layers.remove(uv_map)
            print("Removed duplicate uv_1 maps for object: {}".format(obj.name))
        elif len(uv_1_maps) == 1:
            uv_1_maps[0].name = "uv_1"  # Ensure it's named exactly "uv_1"
            uv_1_exists = True
        
        # Handle UVMap renaming
        if "UVMap" in obj.data.uv_layers:
            obj.data.uv_layers["UVMap"].name = "uv_0"
            print("Renamed existing UV map 'UVMap' to 'uv_0' for object: {}".format(obj.name))
            renamed_uv_map = True
            uv_0_exists = True
        
        # Check and rename existing UV maps
        for uv_map in obj.data.uv_layers:
            if uv_map.name == "uv_0":
                uv_0_exists = True
            elif uv_map.name == "uv_1":
                uv_1_exists = True
            else:
                # Only rename if it's not already uv_0 or uv_1
                if not uv_0_exists:
                    uv_map.name = "uv_0"
                    uv_0_exists = True
                elif not uv_1_exists:
                    uv_map.name = "uv_1"
                    uv_1_exists = True
                renamed_uv_map = True
        
        # Create uv_0 if it doesn't exist
        if not renamed_uv_map and not uv_0_exists:
            obj.data.uv_layers.new(name="uv_0")
            print("Created UV map 'uv_0' for object: {}".format(obj.name))
            popup_messages.append(lambda self, context: self.layout.label(text="uv_0 was created - Make sure you unwrapped your UVs!"))
        elif not renamed_uv_map and uv_0_exists:
            print("UV map 'uv_0' already exists for object: {}".format(obj.name))
            maps_already_exist = True
        
        # Create uv_1 if it doesn't exist
        if not uv_1_exists:
            obj.data.uv_layers.new(name="uv_1")
            print("Created UV map 'uv_1' for object: {}".format(obj.name))
            popup_messages.append(lambda self, context: self.layout.label(text="uv_1 was created (not transferred)."))
        
        if uv_1_exists and uv_0_exists:
            print("UV map 'uv_1' already exists for object: {}".format(obj.name))
            maps_already_exist = True
        
        # Prepare messages
        if renamed_uv_map:
            popup_messages.append(lambda self, context: self.layout.label(text="Existing uv map renamed."))
        
        if maps_already_exist:
            popup_messages.append(lambda self, context: self.layout.label(text="Good to go!"))
        
        # Display popup messages if any
        if popup_messages:
            bpy.context.window_manager.popup_menu(display_popup_list(popup_messages), title="Creator Tools", icon='INFO')
        
        # Exit edit mode after running the UV checker
        bpy.ops.object.mode_set(mode='OBJECT')
        
        return {'FINISHED'}

# Popup helper functions
def display_popup_list(popups):
    def draw(self, context):
        layout = self.layout
        for popup in popups:
            popup(self, context)
    return draw

# Register and unregister functions
def register():
    bpy.utils.register_class(si_uvchecker)

def unregister():
    bpy.utils.unregister_class(si_uvchecker)

if __name__ == "__main__":
    register()