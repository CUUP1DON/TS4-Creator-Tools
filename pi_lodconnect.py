import bpy
from bpy.types import Operator
import bmesh
from mathutils import kdtree
import gpu
from gpu_extras.batch import batch_for_shader
from . import pi_errors

# Check Blender version for GPU API compatibility
BLENDER_VERSION = bpy.app.version
USE_NEW_GPU_API = BLENDER_VERSION >= (4, 0, 0)


# ------------------------------------------------------------------------
# Vertex Layer Utility
# ------------------------------------------------------------------------
def get_vertex_marker_layer(bm):
    """Get or create the custom vertex marker layer"""
    layer = bm.verts.layers.int.get("lod_connect_marker")
    if not layer:
        layer = bm.verts.layers.int.new("lod_connect_marker")
    return layer


# ------------------------------------------------------------------------
# Overlay Drawing
# ------------------------------------------------------------------------
draw_handle = None
_vertex_shader_cache = None
_vertex_batch_cache = None

def draw_marked_vertices():
    global _vertex_shader_cache, _vertex_batch_cache
    
    try:
        obj = bpy.context.active_object
        if not obj or obj.type != 'MESH' or bpy.context.mode != 'EDIT_MESH':
            return

        bm = bmesh.from_edit_mesh(obj.data)
        layer = get_vertex_marker_layer(bm)

        coords = []
        for v in bm.verts:
            if v[layer] == 1:
                # Transform local coordinates to world coordinates
                world_co = obj.matrix_world @ v.co
                coords.append(world_co)

        if coords:
            # Enable depth testing so points appear on the mesh surface
            gpu.state.depth_test_set('LESS_EQUAL')
            gpu.state.blend_set('ALPHA')
            gpu.state.point_size_set(8.0)

            # Use cached shader or create new one
            if not _vertex_shader_cache:
                if USE_NEW_GPU_API:
                    # Blender 4.0+ GPU API - use UNIFORM_COLOR instead of 3D_UNIFORM_COLOR
                    _vertex_shader_cache = gpu.shader.from_builtin("UNIFORM_COLOR")
                else:
                    # Legacy Blender 3.x GPU API
                    _vertex_shader_cache = gpu.shader.from_builtin("3D_UNIFORM_COLOR")

            batch = batch_for_shader(_vertex_shader_cache, 'POINTS', {"pos": coords})
            _vertex_shader_cache.bind()
            _vertex_shader_cache.uniform_float("color", (1.0, 0.0, 1.0, 1.0))  # purple
            batch.draw(_vertex_shader_cache)

            # Reset GPU state
            gpu.state.depth_test_set('NONE')
            gpu.state.blend_set('NONE')
            gpu.state.point_size_set(1.0)
    except Exception:
        # Silently ignore drawing errors to prevent viewport crashes
        pass

def cleanup_vertex_gpu_resources():
    """Clean up vertex overlay GPU resources"""
    global _vertex_shader_cache, _vertex_batch_cache
    try:
        _vertex_shader_cache = None
        _vertex_batch_cache = None
        # Force GPU cleanup
        import gc
        gc.collect()
    except Exception:
        pass


def enable_vertex_overlay():
    global draw_handle
    try:
        if draw_handle is None:
            draw_handle = bpy.types.SpaceView3D.draw_handler_add(
                draw_marked_vertices, (), 'WINDOW', 'POST_VIEW'
            )
    except Exception:
        # Silently ignore overlay registration errors
        pass


def disable_vertex_overlay():
    global draw_handle
    try:
        if draw_handle is not None:
            bpy.types.SpaceView3D.draw_handler_remove(draw_handle, 'WINDOW')
            draw_handle = None
    except Exception:
        # Silently ignore overlay removal errors
        draw_handle = None
    finally:
        # Always clean up GPU resources
        cleanup_vertex_gpu_resources()


def update_vertex_overlay(self, context):
    if context.scene.show_lod_vertex_overlay:
        enable_vertex_overlay()
    else:
        disable_vertex_overlay()


# ------------------------------------------------------------------------
# Operators: Mark / Clear Vertices
# ------------------------------------------------------------------------
class MESH_OT_mark_lod_vertices(bpy.types.Operator):
    """Mark selected vertices for LOD connection"""
    bl_idname = "mesh.mark_lod_vertices"
    bl_label = "Mark LOD Connection Boundary"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            # Validate context and object
            if not context.edit_object:
                pi_errors.ErrorManager.show_error('wrong_mode',
                    custom_message="Please enter Edit Mode first",
                    custom_details=[
                        "Select a mesh object",
                        "Press Tab to enter Edit Mode",
                        "Select vertices to mark for LOD connection"
                    ])
                return {'CANCELLED'}
            
            if context.edit_object.type != 'MESH':
                pi_errors.ErrorManager.show_error('wrong_object_type')
                return {'CANCELLED'}
            
            if context.mode != 'EDIT_MESH':
                pi_errors.ErrorManager.show_error('wrong_mode',
                    custom_message="Must be in Edit Mode to mark vertices",
                    custom_details=[
                        "Press Tab to enter Edit Mode",
                        "Select vertices you want to mark",
                        "Then use this tool"
                    ])
                return {'CANCELLED'}

            bm = bmesh.from_edit_mesh(context.edit_object.data)
            layer = get_vertex_marker_layer(bm)
            count = 0
            
            for v in bm.verts:
                if v.select:
                    v[layer] = 1
                    count += 1
            
            if count == 0:
                pi_errors.ErrorManager.show_error('no_marked_vertices',
                    custom_message="No vertices selected to mark!",
                    custom_details=[
                        "Select vertices in Edit Mode first",
                        "Use Box Select (B) or Circle Select (C)",
                        "Then use this tool to mark them for LOD connection"
                    ])
                return {'CANCELLED'}
            
            bmesh.update_edit_mesh(context.edit_object.data)
            
            # Show success message
            pi_errors.ErrorManager.show_success('operation_complete',
                custom_message=f"Marked {count} vertices for LOD connection",
                custom_details=[
                    "Purple markers now show the selected vertices",
                    "Use 'Connect LOD Vertices' to snap them to body parts"
                ])
            return {'FINISHED'}
            
        except Exception as e:
            pi_errors.ErrorManager.show_error('operation_failed',
                custom_message="Failed to mark vertices",
                additional_info=[f"Error: {str(e)}"])
            return {'CANCELLED'}


class MESH_OT_clear_lod_vertices(bpy.types.Operator):
    """Clear LOD connection markers on selected vertices"""
    bl_idname = "mesh.clear_lod_vertices"
    bl_label = "Clear LOD Connection Boundary"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            # Validate context and object
            if not context.edit_object:
                pi_errors.ErrorManager.show_error('wrong_mode',
                    custom_message="Please enter Edit Mode first",
                    custom_details=[
                        "Select a mesh object",
                        "Press Tab to enter Edit Mode",
                        "Select marked vertices to clear"
                    ])
                return {'CANCELLED'}
            
            if context.edit_object.type != 'MESH':
                pi_errors.ErrorManager.show_error('wrong_object_type')
                return {'CANCELLED'}
            
            if context.mode != 'EDIT_MESH':
                pi_errors.ErrorManager.show_error('wrong_mode',
                    custom_message="Must be in Edit Mode to clear vertex markers",
                    custom_details=[
                        "Press Tab to enter Edit Mode",
                        "Select marked vertices to clear",
                        "Then use this tool"
                    ])
                return {'CANCELLED'}

            bm = bmesh.from_edit_mesh(context.edit_object.data)
            layer = get_vertex_marker_layer(bm)
            count = 0
            
            for v in bm.verts:
                if v.select:
                    v[layer] = 0
                    count += 1
            
            if count == 0:
                pi_errors.ErrorManager.show_error('no_marked_vertices',
                    custom_message="No vertices selected to clear!",
                    custom_details=[
                        "Select marked vertices (purple ones) in Edit Mode",
                        "Use Box Select (B) or Circle Select (C)",
                        "Then use this tool to clear their markers"
                    ])
                return {'CANCELLED'}
            
            bmesh.update_edit_mesh(context.edit_object.data)
            
            # Show success message
            pi_errors.ErrorManager.show_success('operation_complete',
                custom_message=f"Cleared {count} vertex markers",
                custom_details=[
                    "Purple markers removed from selected vertices",
                    "These vertices are no longer marked for LOD connection"
                ])
            return {'FINISHED'}
            
        except Exception as e:
            pi_errors.ErrorManager.show_error('operation_failed',
                custom_message="Failed to clear vertex markers",
                additional_info=[f"Error: {str(e)}"])
            return {'CANCELLED'}


# ------------------------------------------------------------------------
# LOD Vertex Connector Class
# ------------------------------------------------------------------------
class LODVertexConnector:
    def __init__(self, movable_obj, connection_threshold=0.1):
        """
        Initialize the LOD vertex connector
        
        Args:
            movable_obj: Blender object with vertices that can be moved (s4studio_ prefixed)
            connection_threshold: Maximum distance to consider vertices for connection
        """
        self.movable_obj = movable_obj
        self.threshold = connection_threshold
        self.fixed_objects = []
        
        # Find all fixed objects that are visible in viewport
        fixed_name_patterns = ['bottom', 'feet', 'head', 'top', 'bottom_2', 'bottom_2_3']
        for obj in bpy.context.scene.objects:
            if (obj.type == 'MESH' and 
                obj.name.lower() in fixed_name_patterns and 
                obj.visible_get()):
                self.fixed_objects.append(obj)
                
    def get_marked_vertices(self, obj):
        """Get vertices that are manually marked for connection"""
        try:
            # Validate object
            if not obj or obj.type != 'MESH':
                raise ValueError("Invalid mesh object provided")
            
            # Switch to edit mode temporarily
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            
            # Create bmesh from mesh
            bm = bmesh.from_edit_mesh(obj.data)
            bm.verts.ensure_lookup_table()
            
            layer = get_vertex_marker_layer(bm)
            marked_verts = []
            
            for vert in bm.verts:
                if vert[layer] == 1:  # Check if vertex is marked
                    # Convert to world coordinates
                    world_pos = obj.matrix_world @ vert.co
                    marked_verts.append((vert.index, world_pos))
            
            bpy.ops.object.mode_set(mode='OBJECT')
            return marked_verts
            
        except Exception as e:
            # Ensure we're back in object mode if something failed
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except:
                pass
            raise RuntimeError(f"Failed to get marked vertices from {obj.name}: {str(e)}")
    
    def get_all_vertices_from_object(self, obj):
        """Get all vertices from a non-selectable object without entering edit mode"""
        try:
            if not obj or obj.type != 'MESH':
                raise ValueError(f"Invalid mesh object: {obj.name if obj else 'None'}")
            
            vertices = []
            
            # Get mesh data directly without switching modes
            mesh = obj.data
            if not mesh:
                raise ValueError(f"Object {obj.name} has no mesh data")
            
            for i, vert in enumerate(mesh.vertices):
                # Convert to world coordinates
                world_pos = obj.matrix_world @ vert.co
                vertices.append((i, world_pos))
                
            return vertices
            
        except Exception as e:
            raise RuntimeError(f"Failed to get vertices from {obj.name}: {str(e)}")
    
    def get_all_fixed_vertices(self):
        """Get all vertices from all fixed objects"""
        all_fixed_vertices = []
        
        for fixed_obj in self.fixed_objects:
            vertices = self.get_all_vertices_from_object(fixed_obj)
            # Add object reference to each vertex
            for idx, pos in vertices:
                all_fixed_vertices.append((fixed_obj.name, idx, pos))
                
        return all_fixed_vertices
    
    def find_closest_vertices(self, marked_vertices, all_fixed_vertices):
        """Find the closest vertex pairs between marked and all fixed vertices"""
        try:
            if not all_fixed_vertices:
                return []
            
            if not marked_vertices:
                raise ValueError("No marked vertices provided")
                
            # Build KD-tree for all fixed vertices
            kd = kdtree.KDTree(len(all_fixed_vertices))
            for i, (obj_name, idx, pos) in enumerate(all_fixed_vertices):
                if pos is None:
                    raise ValueError(f"Invalid vertex position in {obj_name}")
                kd.insert(pos, i)
            kd.balance()
            
            connections = []
            for mov_idx, mov_pos in marked_vertices:
                if mov_pos is None:
                    continue  # Skip invalid positions
                    
                # Find closest fixed vertex
                closest_pos, closest_i, closest_dist = kd.find(mov_pos)
                
                if closest_dist <= self.threshold:
                    fixed_obj_name, fixed_idx, fixed_pos = all_fixed_vertices[closest_i]
                    connections.append({
                        'movable_idx': mov_idx,
                        'movable_pos': mov_pos,
                        'fixed_obj_name': fixed_obj_name,
                        'fixed_idx': fixed_idx,
                        'fixed_pos': fixed_pos,
                        'distance': closest_dist
                    })
            
            return connections
            
        except Exception as e:
            raise RuntimeError(f"Failed to find vertex connections: {str(e)}")
    
    def connect_vertices(self, connections):
        """Move movable vertices to connect with fixed vertices"""
        try:
            if not connections:
                return 0
            
            if not self.movable_obj or self.movable_obj.type != 'MESH':
                raise ValueError("Invalid movable object")
            
            # Enter edit mode for movable object
            bpy.context.view_layer.objects.active = self.movable_obj
            bpy.ops.object.mode_set(mode='EDIT')
            
            bm = bmesh.from_edit_mesh(self.movable_obj.data)
            bm.verts.ensure_lookup_table()
            
            # Validate vertex indices before moving
            max_vert_idx = len(bm.verts) - 1
            
            # Move vertices
            moved_count = 0
            for connection in connections:
                mov_idx = connection['movable_idx']
                fixed_world_pos = connection['fixed_pos']
                
                # Validate vertex index
                if mov_idx < 0 or mov_idx > max_vert_idx:
                    continue  # Skip invalid indices
                
                # Convert world position to local coordinates of movable object
                try:
                    local_pos = self.movable_obj.matrix_world.inverted() @ fixed_world_pos
                    bm.verts[mov_idx].co = local_pos
                    moved_count += 1
                except:
                    continue  # Skip if matrix inversion fails
            
            # Update mesh
            bmesh.update_edit_mesh(self.movable_obj.data)
            bpy.ops.object.mode_set(mode='OBJECT')
            
            return moved_count
            
        except Exception as e:
            # Ensure we're back in object mode if something failed
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except:
                pass
            raise RuntimeError(f"Failed to connect vertices: {str(e)}")
    
    def merge_marked_vertices_by_distance(self, merge_threshold=0.0001):
        """Merge marked vertices that are close together using merge by distance"""
        try:
            if not self.movable_obj or self.movable_obj.type != 'MESH':
                raise ValueError("Invalid movable object for merging")
            
            bpy.context.view_layer.objects.active = self.movable_obj
            bpy.ops.object.mode_set(mode='EDIT')
            
            bm = bmesh.from_edit_mesh(self.movable_obj.data)
            bm.verts.ensure_lookup_table()
            
            # Get the vertex marker layer
            layer = get_vertex_marker_layer(bm)
            
            # Deselect all vertices first
            bpy.ops.mesh.select_all(action='DESELECT')
            
            # Select only marked vertices
            marked_count = 0
            for vert in bm.verts:
                if vert[layer] == 1:
                    vert.select = True
                    marked_count += 1
            
            merged_count = 0
            if marked_count > 0:
                # Store count before merge
                verts_before = len(bm.verts)
                
                # Merge by distance on selected (marked) vertices only
                result = bpy.ops.mesh.remove_doubles(threshold=merge_threshold)
                
                if result != {'FINISHED'}:
                    raise RuntimeError("Merge by distance operation failed")
                
                # Update bmesh to get new vertex count
                bmesh.update_edit_mesh(self.movable_obj.data)
                bm = bmesh.from_edit_mesh(self.movable_obj.data)
                
                # Calculate how many vertices were merged
                merged_count = verts_before - len(bm.verts)
            
            bmesh.update_edit_mesh(self.movable_obj.data)
            bpy.ops.object.mode_set(mode='OBJECT')
            
            return merged_count
            
        except Exception as e:
            # Ensure we're back in object mode if something failed
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except:
                pass
            raise RuntimeError(f"Failed to merge vertices: {str(e)}")


# ------------------------------------------------------------------------
# Main Connect Operator
# ------------------------------------------------------------------------
class MESH_OT_connect_lod_vertices(Operator):
    """Connect marked LOD vertices to body mesh"""
    bl_idname = "mesh.connect_lod_vertices"
    bl_label = "Connect LOD Vertices"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        try:
            # Validate Blender context
            if not context:
                return {'CANCELLED'}
            
            # Configuration
            connection_threshold = 0.1
            
            # Find s4studio_ prefixed object
            movable_obj = None
            
            # Check selected objects first
            try:
                selected_objects = [obj for obj in context.selected_objects if obj and obj.type == 'MESH']
                
                for obj in selected_objects:
                    if obj.name.startswith("s4studio_"):
                        movable_obj = obj
                        break
            except Exception:
                # If selected_objects fails, continue to check active object
                pass
            
            # If no selected s4studio_ object, check active object
            if not movable_obj and context.active_object:
                if (context.active_object.type == 'MESH' and
                    context.active_object.name.startswith("s4studio_")):
                    movable_obj = context.active_object
            
            if not movable_obj:
                pi_errors.ErrorManager.show_error('file_not_found',
                    custom_message="No S4Studio mesh found!",
                    custom_details=[
                        "Select or make active an object whose name starts with 's4studio_'"
                    ])
                return {'CANCELLED'}
            
            # Validate the movable object
            if not movable_obj.data:
                pi_errors.ErrorManager.show_error('invalid_mesh_data',
                    custom_message=f"Object '{movable_obj.name}' has invalid mesh data!",
                    custom_details=[
                        "The mesh data is corrupt or missing",
                        "Try reloading the object or file"
                    ])
                return {'CANCELLED'}
            
            # Create connector and process
            try:
                connector = LODVertexConnector(movable_obj, connection_threshold)
            except Exception as e:
                pi_errors.ErrorManager.show_error('operation_failed',
                    custom_message="Failed to initialize LOD connector!",
                    additional_info=[f"Error details: {str(e)}"])
                return {'CANCELLED'}
            
            if not connector.fixed_objects:
                pi_errors.ErrorManager.show_error('file_not_found',
                    custom_message="No body objects found in scene!",
                    custom_details=[
                        "Looking for objects named:",
                        "  - bottom, feet, head, top",
                        "  - bottom_2, bottom_2_3",
                        "Make sure these objects are visible in the viewport"
                    ])
                return {'CANCELLED'}
            
            # Get marked vertices from movable object
            try:
                marked_vertices = connector.get_marked_vertices(movable_obj)
            except Exception as e:
                pi_errors.ErrorManager.show_error('operation_failed',
                    custom_message="Failed to access marked vertices!",
                    custom_details=[
                        "This could be due to:",
                        "• Object mode switching issues",
                        "• Corrupt mesh data",
                        "• Locked object"
                    ],
                    additional_info=[f"Error: {str(e)}"])
                return {'CANCELLED'}
            
            if not marked_vertices:
                pi_errors.ErrorManager.show_error('no_marked_vertices')
                return {'CANCELLED'}
            
            # Get all vertices from fixed objects
            try:
                all_fixed_vertices = connector.get_all_fixed_vertices()
            except Exception as e:
                pi_errors.ErrorManager.show_error('operation_failed',
                    custom_message="Failed to access body mesh vertices!",
                    custom_details=[
                        "One of the body objects may have",
                        "corrupt or inaccessible mesh data"
                    ],
                    additional_info=[f"Error: {str(e)}"])
                return {'CANCELLED'}
            
            # Find connections
            try:
                connections = connector.find_closest_vertices(marked_vertices, all_fixed_vertices)
            except Exception as e:
                pi_errors.ErrorManager.show_error('operation_failed',
                    custom_message="Failed to find vertex connections!",
                    custom_details=[
                        "Error in distance calculation or",
                        "KD-tree operations"
                    ],
                    additional_info=[f"Error: {str(e)}"])
                return {'CANCELLED'}
            
            if not connections:
                pi_errors.ErrorManager.show_error('connection_failed',
                    custom_message=f"No connections found for {len(marked_vertices)} marked vertices!",
                    custom_details=[
                        f"Connection distance: {connection_threshold:.2f} units",
                        "",
                        "Solution:",
                        "Move marked vertices closer to body parts",
                        "or increase connection threshold in code"
                    ])
                return {'CANCELLED'}
            
            # Connect vertices
            try:
                connected_count = connector.connect_vertices(connections)
                if connected_count == 0:
                    pi_errors.ErrorManager.show_error('connection_failed')
                    return {'CANCELLED'}
            except Exception as e:
                pi_errors.ErrorManager.show_error('operation_failed',
                    custom_message="Failed to move vertices!",
                    custom_details=[
                        "This could be due to:",
                        "• Object in wrong mode",
                        "• Locked transformations",
                        "• Invalid vertex indices"
                    ],
                    additional_info=[f"Error: {str(e)}"])
                return {'CANCELLED'}
            
            # Merge marked vertices that are close together after connections
            try:
                merged_count = connector.merge_marked_vertices_by_distance()
            except Exception as e:
                # Merging is optional, so continue silently if it fails
                merged_count = 0
            
            # Show success popup
            pi_errors.ErrorManager.show_success('vertices_connected',
                custom_message=f"✓ {movable_obj.name} connected successfully!",
                custom_details=[
                    f"Connected to: {', '.join([obj.name for obj in connector.fixed_objects])}",
                    f"• {connected_count} vertices connected",
                    f"• {merged_count} duplicate vertices merged" if merged_count > 0 else f"• {connected_count} vertices connected"
                ])
            
        except Exception as e:
            # Catch any unexpected errors
            pi_errors.ErrorManager.show_error('operation_failed',
                custom_message="Unexpected error occurred!",
                custom_details=["Please report this error:"],
                additional_info=[str(e)])
            return {'CANCELLED'}
        
        return {'FINISHED'}


# ------------------------------------------------------------------------
# Popup Messages
# ------------------------------------------------------------------------
# Legacy popup functions removed - now using centralized error system from pi_errors.py
# All error handling has been moved to pi_errors.ErrorManager

def display_popup_list(popups):
    """Legacy support function maintained for compatibility"""
    return pi_errors.display_popup_list(popups)


# ------------------------------------------------------------------------
# Register
# ------------------------------------------------------------------------
classes = (
    MESH_OT_mark_lod_vertices,
    MESH_OT_clear_lod_vertices,
    MESH_OT_connect_lod_vertices,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.show_lod_vertex_overlay = bpy.props.BoolProperty(
        name="Show LOD Vertex Markers",
        default=True,
        update=update_vertex_overlay
    )
    enable_vertex_overlay()

def unregister():
    global draw_handle, _vertex_shader_cache, _vertex_batch_cache
    
    # Ensure overlay is disabled before unregistering
    disable_vertex_overlay()
    
    # Force cleanup of all global variables
    try:
        draw_handle = None
        _vertex_shader_cache = None
        _vertex_batch_cache = None
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
                    layer = bm.verts.layers.int.get("lod_connect_marker")
                    if layer:
                        bm.verts.layers.int.remove(layer)
                    
                    # Update the mesh and free bmesh
                    bm.to_mesh(mesh)
                    bm.free()
                except Exception:
                    pass
    except Exception:
        pass
    
    # Clean up scene properties with error handling
    try:
        if hasattr(bpy.types.Scene, 'show_lod_vertex_overlay'):
            del bpy.types.Scene.show_lod_vertex_overlay
    except Exception:
        pass
    
    # Final GPU cleanup
    cleanup_vertex_gpu_resources()
    
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