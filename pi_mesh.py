import bpy
from . import pi_errors

# Legacy popup functions (kept for compatibility)
def select_obj(self, context):
    pi_errors.ErrorManager.show_error('no_object_selected')

def exit_edit(self, context):
    pi_errors.ErrorManager.show_error('exit_edit_mode')

def sfs_not_found(self, context):
    pi_errors.ErrorManager.show_error('file_not_found',
                                     custom_message="s4studio_mesh_1 not found.")

def ref_not_found(self, context):
    pi_errors.ErrorManager.show_error('file_not_found',
                                     custom_message="REF not found.")

def no_weight_groups(self, context):
    pi_errors.ErrorManager.show_error('no_weight_groups')

def weight_trans(self, context):
    pi_errors.ErrorManager.show_success('weights_transferred')

def sub_succ(self, context):
    pi_errors.ErrorManager.show_success('mesh_subdivided')

def wesmo(self, context):
    pi_errors.ErrorManager.show_success('weights_smoothed')

def wesmonog(self, context):
    pi_errors.ErrorManager.show_error('no_weight_groups')

def limwesucc(self, context):
    pi_errors.ErrorManager.show_success('weights_limited')

def rbmbdsucc(self, context):
    pi_errors.ErrorManager.show_success('doubles_removed')

def ttqsucc(self, context):
    pi_errors.ErrorManager.show_success('faces_converted')

def linkrigsucc(self, context):
    pi_errors.ErrorManager.show_success('rig_linked')

def norig(self, context):
    pi_errors.ErrorManager.show_error('no_rig_found')

# Legacy helper function
def display_popup_list(popups):
    return pi_errors.display_popup_list(popups)

# Remove Doubles
class rdmbd(bpy.types.Operator):
    bl_idname = "object.rdmbd"
    bl_label = "Remove Doubles"
    bl_description = "Remove Doubles/Merge by distance"

    threshold: bpy.props.FloatProperty(
        name="Merge Distance",
        description="Distance within which vertices are merged",
        default=0.0001,
        min=0.000001,
        max=50.0,
        step=0.01,
        precision=6
    )

    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Remove Doubles")
        
        # Check if there's an active object
        if not context.active_object:
            pi_errors.ErrorManager.show_error('no_object_selected')
            return {'CANCELLED'}
        
        # Check if object is hidden
        if context.active_object.hide_get():
            pi_errors.ErrorManager.show_error('no_object_selected')
            return {'CANCELLED'}
        
        # Check if object is a mesh
        if context.active_object.type != 'MESH':
            pi_errors.ErrorManager.show_error('wrong_object_type')
            return {'CANCELLED'}
        
        bpy.ops.object.mode_set(mode='EDIT')
        
        if context.active_object and context.active_object.mode == 'EDIT':
            obj = context.active_object
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles(threshold=self.threshold)
            
            pi_errors.ErrorManager.show_success('doubles_removed')
        else:
            pi_errors.ErrorManager.show_error('exit_edit_mode')
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        # Skip dialog and use fixed threshold of 0.0001
        self.threshold = 0.0001
        return self.execute(context)

# Tris To Quads
class quadfa(bpy.types.Operator):
    bl_idname = "object.quadfa"
    bl_label = "Tris to Quads"
    bl_description = "Tris to Quads"

    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Tris to Quads")
        
        # Check if there's an active object
        if not context.active_object:
            pi_errors.ErrorManager.show_error('no_object_selected')
            return {'CANCELLED'}
        
        # Check if object is hidden
        if context.active_object.hide_get():
            pi_errors.ErrorManager.show_error('no_object_selected')
            return {'CANCELLED'}
        
        # Check if object is a mesh
        if context.active_object.type != 'MESH':
            pi_errors.ErrorManager.show_error('wrong_object_type')
            return {'CANCELLED'}
        
        bpy.ops.object.mode_set(mode='EDIT')
        
        if context.active_object and context.active_object.mode == 'EDIT':
            obj = context.active_object
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.tris_convert_to_quads()
            
            pi_errors.ErrorManager.show_success('faces_converted')
        else:
            pi_errors.ErrorManager.show_error('exit_edit_mode')
            return {'CANCELLED'}

        return {'FINISHED'}

# Triangulate Faces
class trifa(bpy.types.Operator):
    bl_idname = "object.trifa"
    bl_label = "Triangulate Faces"
    bl_description = "Triangulate Faces"

    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Triangulate Faces")
        
        # Check if there's an active object
        if not context.active_object:
            pi_errors.ErrorManager.show_error('no_object_selected')
            return {'CANCELLED'}
        
        # Check if object is hidden
        if context.active_object.hide_get():
            pi_errors.ErrorManager.show_error('no_object_selected')
            return {'CANCELLED'}
        
        # Check if object is a mesh
        if context.active_object.type != 'MESH':
            pi_errors.ErrorManager.show_error('wrong_object_type')
            return {'CANCELLED'}
        
        bpy.ops.object.mode_set(mode='EDIT')
        
        if context.active_object and context.active_object.mode == 'EDIT':
            obj = context.active_object
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')

            pi_errors.ErrorManager.show_success('faces_converted')
        else:
            pi_errors.ErrorManager.show_error('exit_edit_mode')
            return {'CANCELLED'}

        return {'FINISHED'}
    
# Subdivide
class sii_subdivision(bpy.types.Operator):
    bl_idname = "object.sii_subdivision"
    bl_label = "Subdivision"
    bl_description = "Apply subdivision to the REF mesh"

    levels: bpy.props.IntProperty(name="Subdivision Levels", default=1, min=1, max=10)

    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Subdivide")
        bpy.ops.object.mode_set(mode='OBJECT')
    
        for obj in context.selected_objects:
            if obj.mode == 'EDIT':
                bpy.ops.object.mode_set(mode='OBJECT')

        for obj in context.selected_objects:
            if obj.hide_get():
                pi_errors.ErrorManager.show_error('no_object_selected')
                return {'CANCELLED'}
        obj = bpy.data.objects.get("REF")
        if obj is None:
            pi_errors.ErrorManager.show_error('file_not_found',
                custom_message="REF object not found",
                custom_details=["Load a REF object first",
                               "Make sure REF object is visible"])
            return {'CANCELLED'}

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        modifier = obj.modifiers.new(name="Subdivision", type='SUBSURF')
        modifier.levels = self.levels
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        
        pi_errors.ErrorManager.show_success('mesh_subdivided')
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Subdivision Settings", icon='MOD_SUBSURF')
        layout.separator()
        
        col = layout.column(align=True)
        col.label(text="Levels:")
        col.prop(self, "levels", text="", slider=True)
        
        layout.separator()
        row = layout.row()
        row.label(text="Target: REF mesh", icon='MESH_DATA')

# Register all classes
def register():
    bpy.utils.register_class(rdmbd)
    bpy.utils.register_class(quadfa)
    bpy.utils.register_class(trifa)
    bpy.utils.register_class(sii_subdivision)

def unregister():
    bpy.utils.unregister_class(rdmbd)
    bpy.utils.unregister_class(quadfa)
    bpy.utils.unregister_class(trifa)
    bpy.utils.unregister_class(sii_subdivision)

if __name__ == "__main__":
    register()