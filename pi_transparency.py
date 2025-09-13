import bpy
import bmesh
import gpu
from gpu_extras.batch import batch_for_shader
from . import pi_errors


# ------------------------------------------------------------------------
# Strip Layer Utility
# ------------------------------------------------------------------------
def get_strip_layer(bm):
    """Get or create the custom strip marker layer"""
    layer = bm.edges.layers.int.get("strip_marker")
    if not layer:
        layer = bm.edges.layers.int.new("strip_marker")
    return layer


# ------------------------------------------------------------------------
# Overlay Drawing
# ------------------------------------------------------------------------
draw_handle = None
_shader_cache = None
_batch_cache = None

def draw_strip_edges():
    global _shader_cache, _batch_cache
    
    try:
        obj = bpy.context.active_object
        if not obj or obj.type != 'MESH' or bpy.context.mode != 'EDIT_MESH':
            return

        bm = bmesh.from_edit_mesh(obj.data)
        layer = get_strip_layer(bm)

        coords = []
        for e in bm.edges:
            if e[layer] == 1:
                # Transform local coordinates to world coordinates
                world_co1 = obj.matrix_world @ e.verts[0].co
                world_co2 = obj.matrix_world @ e.verts[1].co
                coords.append(world_co1)
                coords.append(world_co2)

        if coords:
            # Enable depth testing so lines appear on the mesh surface
            import gpu
            gpu.state.depth_test_set('LESS_EQUAL')
            gpu.state.blend_set('ALPHA')
            
            # Use cached shader or create new one
            if not _shader_cache:
                _shader_cache = gpu.shader.from_builtin("3D_UNIFORM_COLOR")
            
            batch = batch_for_shader(_shader_cache, 'LINES', {"pos": coords})
            _shader_cache.bind()
            _shader_cache.uniform_float("color", (0.7, 0.2, 0.9, 1.0))  # purple
            batch.draw(_shader_cache)
            
            # Reset GPU state
            gpu.state.depth_test_set('NONE')
            gpu.state.blend_set('NONE')
    except Exception:
        # Silently ignore drawing errors to prevent viewport crashes
        pass

def cleanup_gpu_resources():
    """Clean up GPU resources"""
    global _shader_cache, _batch_cache
    try:
        _shader_cache = None
        _batch_cache = None
        # Force GPU cleanup
        import gc
        gc.collect()
    except Exception:
        pass


def enable_strip_overlay():
    global draw_handle
    if draw_handle is None:
        draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_strip_edges, (), 'WINDOW', 'POST_VIEW'
        )


def disable_strip_overlay():
    global draw_handle
    try:
        if draw_handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(draw_handle, 'WINDOW')
            draw_handle = None
    except Exception:
        # Silently ignore overlay removal errors to prevent crashes
        draw_handle = None
    finally:
        # Always clean up GPU resources
        cleanup_gpu_resources()


def update_strip_overlay(self, context):
    if context.scene.show_strip_overlay:
        enable_strip_overlay()
    else:
        disable_strip_overlay()


# ------------------------------------------------------------------------
# Operators: Mark / Clear Strip
# ------------------------------------------------------------------------
class MESH_OT_mark_strip(bpy.types.Operator):
    """Mark selected edges as strip boundaries"""
    bl_idname = "mesh.mark_strip"
    bl_label = "Mark Boundary"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Validate context and object
        if not context.edit_object:
            pi_errors.ErrorManager.show_error('wrong_mode',
                custom_message="Please enter Edit Mode on a mesh object",
                custom_details=[
                    "Select a mesh object",
                    "Press Tab to enter Edit Mode",
                    "Select edges you want to mark as strip boundaries"
                ])
            return {'CANCELLED'}
        
        if context.edit_object.type != 'MESH':
            pi_errors.ErrorManager.show_error('wrong_object_type')
            return {'CANCELLED'}
            
        if context.mode != 'EDIT_MESH':
            pi_errors.ErrorManager.show_error('wrong_mode',
                custom_message="Must be in Edit Mode to mark strip boundaries",
                custom_details=[
                    "Press Tab to enter Edit Mode",
                    "Select edges to mark as strip boundaries"
                ])
            return {'CANCELLED'}
        
        try:
            bm = bmesh.from_edit_mesh(context.edit_object.data)
            layer = get_strip_layer(bm)
            count = 0
            for e in bm.edges:
                if e.select:
                    e[layer] = 1
                    count += 1
            
            if count == 0:
                pi_errors.ErrorManager.show_error('no_marked_vertices',
                    custom_message="No edges selected to mark!",
                    custom_details=[
                        "Select edges in Edit Mode first",
                        "Use Alt+Click to select edge loops",
                        "Then use this tool to mark them as strip boundaries"
                    ])
                return {'CANCELLED'}
            
            bmesh.update_edit_mesh(context.edit_object.data)
            pi_errors.ErrorManager.show_success('operation_complete',
                custom_message=f"Marked {count} edges as strip boundaries",
                custom_details=[
                    "These edges will be used to split the mesh for transparency",
                    "Purple lines show the marked boundaries",
                    "Use 'Fix Transparency' to apply the fix"
                ])
            return {'FINISHED'}
            
        except Exception as e:
            pi_errors.ErrorManager.show_error('operation_failed',
                custom_message="Failed to mark strip boundaries",
                additional_info=[f"Error: {str(e)}"])
            return {'CANCELLED'}


class MESH_OT_clear_strip(bpy.types.Operator):
    """Clear strip boundaries on selected edges"""
    bl_idname = "mesh.clear_strip"
    bl_label = "Clear Boundary"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Validate context and object
        if not context.edit_object:
            pi_errors.ErrorManager.show_error('wrong_mode',
                custom_message="Please enter Edit Mode on a mesh object",
                custom_details=[
                    "Select a mesh object",
                    "Press Tab to enter Edit Mode",
                    "Select strip boundary edges to clear"
                ])
            return {'CANCELLED'}
        
        if context.edit_object.type != 'MESH':
            pi_errors.ErrorManager.show_error('wrong_object_type')
            return {'CANCELLED'}
            
        if context.mode != 'EDIT_MESH':
            pi_errors.ErrorManager.show_error('wrong_mode',
                custom_message="Must be in Edit Mode to clear strip boundaries",
                custom_details=[
                    "Press Tab to enter Edit Mode",
                    "Select marked edges to clear their boundaries"
                ])
            return {'CANCELLED'}
        
        try:
            bm = bmesh.from_edit_mesh(context.edit_object.data)
            layer = get_strip_layer(bm)
            count = 0
            for e in bm.edges:
                if e.select:
                    e[layer] = 0
                    count += 1
            
            if count == 0:
                pi_errors.ErrorManager.show_error('no_marked_vertices',
                    custom_message="No edges selected to clear!",
                    custom_details=[
                        "Select marked edges (purple lines) in Edit Mode",
                        "Use Alt+Click to select edge loops",
                        "Then use this tool to clear their strip boundaries"
                    ])
                return {'CANCELLED'}
            
            bmesh.update_edit_mesh(context.edit_object.data)
            pi_errors.ErrorManager.show_success('operation_complete',
                custom_message=f"Cleared {count} strip boundary markers",
                custom_details=[
                    "Purple boundary lines removed from selected edges",
                    "These edges are no longer marked as strip boundaries"
                ])
            return {'FINISHED'}
            
        except Exception as e:
            pi_errors.ErrorManager.show_error('operation_failed',
                custom_message="Failed to clear strip boundaries",
                additional_info=[f"Error: {str(e)}"])
            return {'CANCELLED'}


# ------------------------------------------------------------------------
# Operator: Transparency Fix
# ------------------------------------------------------------------------
class MESH_OT_transparency_fix(bpy.types.Operator):
    """Fix transparency rendering issues using marked strip boundaries. Requires mesh object in Object mode with marked boundaries"""
    bl_idname = "mesh.transparency_fix"
    bl_label = "Fix Transparency"
    bl_description = "Fix transparency rendering issues using marked strip boundaries (Object mode required)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == 'MESH'
            and context.mode == 'OBJECT'
        )

    def execute(self, context):
        obj = context.active_object
        mesh = obj.data

        # Save transforms
        orig_loc, orig_rot, orig_scale = obj.location.copy(), obj.rotation_euler.copy(), obj.scale.copy()

        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(mesh)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        bm.faces.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        layer = get_strip_layer(bm)

        # Gather edges manually marked
        marked_edges = [e for e in bm.edges if e[layer] == 1]

        if not marked_edges:
            pi_errors.ErrorManager.show_error('no_marked_vertices',
                custom_message="No strips found for transparency fix.",
                custom_details=[
                    "Use 'Mark Boundary' button to mark edges first",
                    "At least one edge must be marked to split the mesh"
                ])
            bpy.ops.object.mode_set(mode='OBJECT')
            return {'CANCELLED'}

        # Split at marked edges
        bpy.ops.mesh.select_all(action='DESELECT')
        for e in marked_edges:
            e.select = True
        bmesh.update_edit_mesh(mesh)
        bpy.ops.mesh.edge_split()

        # Separate → Join → Cleanup
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.separate(type='LOOSE')
        bpy.ops.object.mode_set(mode='OBJECT')
        parts = bpy.context.selected_objects[:]

        if len(parts) <= 1:
            pi_errors.ErrorManager.show_error('operation_failed',
                custom_message="Mesh did not split into strips properly.",
                custom_details=[
                    "The marked edges may not form proper boundaries",
                    "Try marking different edges or check mesh topology",
                    "Make sure marked edges create separate sections"
                ])
            return {'CANCELLED'}

        bpy.ops.object.select_all(action='DESELECT')
        for p in parts:
            p.select_set(True)
        bpy.context.view_layer.objects.active = parts[0]
        bpy.ops.object.join()
        final = bpy.context.active_object

        final.location, final.rotation_euler, final.scale = orig_loc, orig_rot, orig_scale

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=0.0001)
        bpy.ops.mesh.mark_sharp(clear=True)
        bpy.ops.object.mode_set(mode='OBJECT')

        pi_errors.ErrorManager.show_success('operation_complete',
            custom_message=f"Transparency fix complete! Joined {len(parts)} strips.",
            custom_details=[
                "Your mesh is now optimized for transparency rendering",
                "The strips have been processed and rejoined properly"
            ])
        return {'FINISHED'}


# ------------------------------------------------------------------------
# Register
# ------------------------------------------------------------------------
classes = (
    MESH_OT_mark_strip,
    MESH_OT_clear_strip,
    MESH_OT_transparency_fix,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.show_strip_overlay = bpy.props.BoolProperty(
        name="Show Strip Boundaries",
        default=True,
        update=update_strip_overlay
    )
    enable_strip_overlay()


def unregister():
    global draw_handle, _shader_cache, _batch_cache
    
    # Ensure overlay is disabled before unregistering
    disable_strip_overlay()
    
    # Force cleanup of all global variables
    try:
        draw_handle = None
        _shader_cache = None
        _batch_cache = None
    except Exception:
        pass
    
    # Clean up custom data layers from all meshes
    try:
        for mesh in bpy.data.meshes:
            if mesh:
                try:
                    # Force update to object mode to safely access bmesh
                    bm = bmesh.new()
                    bm.from_mesh(mesh)
                    
                    # Remove our custom layer if it exists
                    layer = bm.edges.layers.int.get("strip_marker")
                    if layer:
                        bm.edges.layers.int.remove(layer)
                    
                    # Update the mesh and free bmesh
                    bm.to_mesh(mesh)
                    bm.free()
                except Exception:
                    pass
    except Exception:
        pass
    
    # Clean up scene properties with error handling
    try:
        if hasattr(bpy.types.Scene, 'show_strip_overlay'):
            del bpy.types.Scene.show_strip_overlay
    except Exception:
        pass
    
    # Final GPU cleanup
    cleanup_gpu_resources()
    
    # Force garbage collection
    try:
        import gc
        gc.collect()
    except Exception:
        pass
    
    # Unregister classes with error handling
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass


if __name__ == "__main__":
    register()