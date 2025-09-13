import bpy
from . import pi_errors

# Weight Transfer
class siiii_weights(bpy.types.Operator):
    bl_idname = "object.siiii_weights"
    bl_label = "Weight Transfer"
    bl_description = "Transfer weight data from REF mesh to your mesh"

    def execute(self, context):
        obj = bpy.data.objects.get("s4studio_mesh_1")
        if obj is None:
            pi_errors.ErrorManager.show_error('file_not_found',
                custom_message="s4studio_mesh_1 object not found",
                custom_details=["Make sure S4Studio mesh is in your scene",
                               "Check object naming and visibility"])
            return {'CANCELLED'}
            
        obj = bpy.data.objects.get("REF")
        if obj is None:
            pi_errors.ErrorManager.show_error('file_not_found',
                custom_message="REF object not found",
                custom_details=["Load a REF object first",
                               "Make sure REF object is visible"])
            return {'CANCELLED'}
            
        obj = bpy.data.objects.get("REF")
        if obj and not obj.vertex_groups:
            pi_errors.show_error('no_weight_groups')
            return {'CANCELLED'}
            
        self.siiii_weights()
        return {'FINISHED'}

    def siiii_weights(self):
        bpy.ops.ed.undo_push(message="Creator Tools: Weight Transfer")
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        # Get the target object
        target_obj = bpy.data.objects['s4studio_mesh_1']
        source_obj = bpy.data.objects['REF']
        
        # Clear existing vertex groups on target to prevent duplicates
        target_obj.vertex_groups.clear()
        
        # Select objects for weight transfer
        for o in bpy.data.objects:
            if o.name in ("s4studio_mesh_1"):
                o.select_set(True)
                
        bpy.context.view_layer.objects.active = target_obj

        for o in bpy.data.objects:
            if o.name in ("REF", "s4studio_mesh_1"):
                o.select_set(True)

        bpy.ops.paint.weight_paint_toggle()
        
        # Single weight transfer operation with proper settings
        bpy.ops.object.data_transfer(
            use_reverse_transfer=True, 
            data_type='VGROUP_WEIGHTS',
            use_create=True,
            vert_mapping='NEAREST',
            layers_select_src='NAME',
            layers_select_dst='ALL'
        )
        
        bpy.ops.object.vertex_group_limit_total()
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # REF mesh deletion removed from here
        pi_errors.show_weights_transferred()


# Delete REF Mesh
class delete_ref_mesh(bpy.types.Operator):
    bl_idname = "object.delete_ref_mesh"
    bl_label = "Delete REF Mesh"
    bl_description = "Delete the REF mesh from the scene"

    def execute(self, context):
        mesh_ref = bpy.data.objects.get("REF")
        if mesh_ref:
            bpy.ops.ed.undo_push(message="Creator Tools: Delete REF Mesh")
            bpy.data.objects.remove(mesh_ref, do_unlink=True)
            pi_errors.ErrorManager.show_success('operation_complete',
                custom_message="REF mesh deleted successfully",
                custom_details=["The reference mesh has been removed from the scene"])
        else:
            pi_errors.ErrorManager.show_error('file_not_found',
                custom_message="REF object not found",
                custom_details=["No REF mesh to delete",
                               "Make sure REF object exists in the scene"])
            return {'CANCELLED'}
            
        return {'FINISHED'}


# Smooth Weights
class smoothwe(bpy.types.Operator):
    bl_idname = "object.smoothwe"
    bl_label = "Smooth Weights"
    bl_description = "Smooth weights (use sparingly)"

    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Smooth Weights")
        
        # Validate active object before attempting mode change
        if not context.active_object:
            pi_errors.ErrorManager.show_error('no_object_selected',
                custom_message="No object selected for weight smoothing",
                custom_details=[
                    "Select a mesh object with vertex groups",
                    "Make sure the object is rigged or has weight data"
                ])
            return {'CANCELLED'}
            
        obj = context.active_object
        if obj.type != 'MESH':
            pi_errors.show_error('wrong_object_type')
            return {'CANCELLED'}
            
        # Check if object has vertex groups
        if not obj.vertex_groups:
            pi_errors.ErrorManager.show_error('no_weight_groups',
                custom_message="Object has no vertex groups to smooth",
                custom_details=[
                    "The object needs to be rigged or have weight data",
                    "Use the weight transfer tool first if needed"
                ])
            return {'CANCELLED'}
        
        try:
            # Now safe to change modes
            bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
        except Exception as e:
            pi_errors.ErrorManager.show_error('blender_context_error',
                custom_message="Cannot enter Weight Paint mode",
                custom_details=[
                    "Make sure the object is properly selected",
                    "Try clicking on the object again"
                ],
                additional_info=[f"Error: {str(e)}"])
            return {'CANCELLED'}

        if context.active_object and context.active_object.mode == 'WEIGHT_PAINT':
            obj = context.active_object
            if obj.type == 'MESH' and obj.data.vertices:
                try:
                    # Disable mirror if it's enabled
                    if obj.data.use_mirror_x:
                        obj.data.use_mirror_x = False
                    if obj.data.use_mirror_y:
                        obj.data.use_mirror_y = False
                    if obj.data.use_mirror_z:
                        obj.data.use_mirror_z = False
                    bpy.ops.object.vertex_group_smooth(group_select_mode='ALL', factor=0.5, repeat=3)
                    pi_errors.show_success('weights_smoothed')
                except Exception as e:
                    pi_errors.ErrorManager.show_error('operation_failed',
                        custom_message="Failed to smooth weights",
                        additional_info=[f"Error: {str(e)}"])
                    return {'CANCELLED'}
            else:
                pi_errors.ErrorManager.show_error('no_weight_groups',
                    custom_message="No mesh data found or object not valid",
                    custom_details=["Make sure you have a valid mesh object",
                                   "Check that the object has proper mesh data"])
                return {'CANCELLED'}
        else:
            pi_errors.ErrorManager.show_error('blender_context_error',
                custom_message="Could not enter Weight Paint mode",
                custom_details=[
                    "The object may not support weight painting",
                    "Make sure you have a rigged mesh selected"
                ])
            return {'CANCELLED'}

        return {'FINISHED'}


# Limit Total Weight
class limwe(bpy.types.Operator):
    bl_idname = "object.limwe"
    bl_label = "Limit Weights"
    bl_description = "Limit the number of weights per vertex"

    limit_count: bpy.props.IntProperty(
        name="Limit Count",
        description="Number of weights to limit per vertex",
        default=4,
        min=1,
        max=8
    )

    def execute(self, context):
        bpy.ops.ed.undo_push(message="Limit Weights Per Vertex")

        # Validate active object before checking mode
        if not context.active_object:
            pi_errors.ErrorManager.show_error('no_object_selected',
                custom_message="No object selected for weight limiting",
                custom_details=[
                    "Select a mesh object with vertex groups",
                    "Make sure the object is rigged or has weight data"
                ])
            return {'CANCELLED'}
            
        obj = context.active_object
        if obj.type != 'MESH':
            pi_errors.show_error('wrong_object_type')
            return {'CANCELLED'}
            
        # Check if object has vertex groups
        if not obj.vertex_groups:
            pi_errors.ErrorManager.show_error('no_weight_groups',
                custom_message="Selected object has no vertex groups to limit",
                custom_details=["The object needs vertex groups to limit weights",
                               "Make sure the object has been rigged or has weight data"])
            return {'CANCELLED'}

        # Check if already in weight paint mode, if not try to enter it
        if context.active_object.mode != 'WEIGHT_PAINT':
            try:
                bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
            except Exception as e:
                pi_errors.ErrorManager.show_error('blender_context_error',
                    custom_message="Cannot enter Weight Paint mode",
                    custom_details=[
                        "Make sure the object is properly selected",
                        "The object needs to be rigged to enter Weight Paint mode",
                        "Try selecting the object again"
                    ],
                    additional_info=[f"Error: {str(e)}"])
                return {'CANCELLED'}

        # Now we're in weight paint mode, perform the operation
        if context.active_object and context.active_object.mode == 'WEIGHT_PAINT':
            obj = context.active_object
            if obj.type == 'MESH' and obj.data.vertices:
                try:
                    # Limit weights per vertex using the given count
                    bpy.ops.object.vertex_group_limit_total(limit=self.limit_count)

                    # Show success message
                    pi_errors.ErrorManager.show_success('weights_limited',
                        custom_message=f"Limited weights to {self.limit_count} per vertex",
                        custom_details=[
                            "Each vertex now influences a maximum number of bones",
                            "This improves performance and prevents deformation issues"
                        ])
                    return {'FINISHED'}
                except Exception as e:
                    pi_errors.ErrorManager.show_error('operation_failed',
                        custom_message="Failed to limit vertex weights",
                        additional_info=[f"Error: {str(e)}"])
                    return {'CANCELLED'}
            else:
                pi_errors.ErrorManager.show_error('invalid_mesh_data')
                return {'CANCELLED'}
        else:
            pi_errors.ErrorManager.show_error('blender_context_error',
                custom_message="Could not access Weight Paint mode",
                custom_details=[
                    "The object may not support weight painting",
                    "Make sure you have a rigged mesh selected"
                ])
            return {'CANCELLED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        col = layout.column()
        col.label(text="Limit the number of weights per vertex:")
        col.separator()
        
        row = col.row()
        row.prop(self, "limit_count", text="Max Weights")
        
        col.separator()
        col.label(text="The Sims 4 has a limit of 4 weights per vertex.", icon='INFO')


# Registration
def register():
    bpy.utils.register_class(siiii_weights)
    bpy.utils.register_class(delete_ref_mesh)
    bpy.utils.register_class(smoothwe)
    bpy.utils.register_class(limwe)


def unregister():
    bpy.utils.unregister_class(siiii_weights)
    bpy.utils.unregister_class(delete_ref_mesh)
    bpy.utils.unregister_class(smoothwe)
    bpy.utils.unregister_class(limwe)


if __name__ == "__main__":
    register()