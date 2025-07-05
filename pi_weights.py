import bpy

# Popup messages - you may need to adjust these based on your existing popup system
def display_popup_list(popups):
    def draw(self, context):
        for popup in popups:
            self.layout.label(text=popup)
    return draw

# Define popup messages (adjust these to match your existing ones)
sfs_not_found = "s4studio_mesh_1 object not found"
ref_not_found = "REF object not found"
no_weight_groups = "REF object has no vertex groups"
weight_trans = "Weight transfer completed successfully"
wesmo = "Weights smoothed successfully"
wesmonog = "No mesh data found or object not valid"
select_obj = "Please select an object and enter weight paint mode"
limwesucc = "Weight limit applied successfully"
no_vertex_groups = "Selected object has no vertex groups to limit"
ref_deleted = "REF mesh deleted successfully"

# Weight Transfer
class siiii_weights(bpy.types.Operator):
    bl_idname = "object.siiii_weights"
    bl_label = "Weight Transfer"
    bl_description = "Transfer weight data from REF mesh to your mesh"

    def execute(self, context):
        obj = bpy.data.objects.get("s4studio_mesh_1")
        if obj is None:
            popups = [sfs_not_found]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
            return {'CANCELLED'}
            
        obj = bpy.data.objects.get("REF")
        if obj is None:
            popups = [ref_not_found]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
            return {'CANCELLED'}
            
        obj = bpy.data.objects.get("REF")
        if obj and not obj.vertex_groups:
            popups = [no_weight_groups]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
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
        popups = [weight_trans]
        bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='INFO')


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
            popups = [ref_deleted]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='INFO')
        else:
            popups = [ref_not_found]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
            return {'CANCELLED'}
            
        return {'FINISHED'}


# Smooth Weights
class smoothwe(bpy.types.Operator):
    bl_idname = "object.smoothwe"
    bl_label = "Smooth Weights"
    bl_description = "Smooth weights (use sparingly)"

    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Smooth Weights")
        bpy.ops.object.mode_set(mode='WEIGHT_PAINT')

        if context.active_object and context.active_object.mode == 'WEIGHT_PAINT':
            obj = context.active_object
            if obj.type == 'MESH' and obj.data.vertices:
                # Disable mirror if it's enabled
                if obj.data.use_mirror_x:
                    obj.data.use_mirror_x = False
                if obj.data.use_mirror_y:
                    obj.data.use_mirror_y = False
                if obj.data.use_mirror_z:
                    obj.data.use_mirror_z = False
                bpy.ops.object.vertex_group_smooth(group_select_mode='ALL', factor=0.5, repeat=3)
                popups = [wesmo]
                bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='INFO')
            else:
                popups = [wesmonog]
                bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
                return {'CANCELLED'}
        else:
            popups = [select_obj]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
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

        # Check if the active object is valid and in weight paint mode
        if context.active_object and context.active_object.mode == 'WEIGHT_PAINT':
            obj = context.active_object

            # Check if the object has vertex data
            if obj.type == 'MESH' and obj.data.vertices:
                # Check if the object has vertex groups
                if not obj.vertex_groups:
                    popups = [no_vertex_groups]
                    bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
                    return {'CANCELLED'}
                
                # Limit weights per vertex using the given count
                bpy.ops.object.vertex_group_limit_total(limit=self.limit_count)

                # Show success message
                popups = [limwesucc]
                bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='INFO')
                return {'FINISHED'}
            else:
                popups = [wesmonog]
                bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
        else:
            popups = [select_obj]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')

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