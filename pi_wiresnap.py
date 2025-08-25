import bpy
from bpy.types import Operator

class MESH_OT_setup_wireframe_snap(Operator):
    """Turn on wireframe mode."""
    bl_idname = "mesh.setup_wireframe_snap"
    bl_label = "Setup Wireframe + Snap"
    bl_options = {'REGISTER', 'UNDO'}
   
    def execute(self, context):
        # Set viewport shading to wireframe
        context.space_data.shading.type = 'WIREFRAME'
       
        # Turn off X-ray
        context.space_data.shading.show_xray = False
       
        # Turn on snap
        context.scene.tool_settings.use_snap = True
       
        # Set snap to vertex
        context.scene.tool_settings.snap_elements = {'VERTEX'}
       
        # Show success popup
        bpy.context.window_manager.popup_menu(display_popup_list([wireframe_success]), title="Creator Tools", icon='SNAP_VERTEX')
       
        return {'FINISHED'}

class MESH_OT_turn_off_wireframe(Operator):
    """Turn off wireframe mode."""
    bl_idname = "mesh.turn_off_wireframe"
    bl_label = "Turn Off Wireframe"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Set viewport shading to solid
        context.space_data.shading.type = 'SOLID'
        
        # Turn off snap
        context.scene.tool_settings.use_snap = False
        
        # Show success popup
        bpy.context.window_manager.popup_menu(display_popup_list([wireframe_off_success]), title="Creator Tools", icon='SHADING_SOLID')
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(MESH_OT_setup_wireframe_snap)
    bpy.utils.register_class(MESH_OT_turn_off_wireframe)

def unregister():
    bpy.utils.unregister_class(MESH_OT_setup_wireframe_snap)
    bpy.utils.unregister_class(MESH_OT_turn_off_wireframe)

def wireframe_success(self, context):
    self.layout.label(text="Wireframe mode on. Vertex snapping enabled.")

def wireframe_off_success(self, context):
    self.layout.label(text="Wireframe mode off. Vertex snapping disabled.")

def display_popup_list(popups):
    def draw(self, context):
        layout = self.layout
        for popup in popups:
            popup(self, context)
    return draw