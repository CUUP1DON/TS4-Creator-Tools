import bpy
from bpy.types import Operator

class MESH_OT_setup_wireframe_snap(Operator):
    """Setup viewport for wireframe with vertex snap"""
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

def wireframe_success(self, context):
    self.layout.label(text="Viewport set to wireframe with vertex snap enabled.")

def display_popup_list(popups):
    def draw(self, context):
        layout = self.layout
        for popup in popups:
            popup(self, context)
    return draw

def register():
    bpy.utils.register_class(MESH_OT_setup_wireframe_snap)

def unregister():
    bpy.utils.unregister_class(MESH_OT_setup_wireframe_snap)