import bpy
from bpy.types import Operator
import bmesh
from mathutils import kdtree

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
                
    def get_boundary_vertices(self, obj):
        """Get vertices that are on the boundary/edge of the mesh"""
        # Switch to edit mode temporarily
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Create bmesh from mesh
        bm = bmesh.from_edit_mesh(obj.data)
        bm.edges.ensure_lookup_table()
        bm.verts.ensure_lookup_table()
        
        boundary_verts = []
        for vert in bm.verts:
            # Check if vertex is on boundary (has edges that are not shared by 2 faces)
            is_boundary = any(len(edge.link_faces) == 1 for edge in vert.link_edges)
            if is_boundary:
                # Convert to world coordinates
                world_pos = obj.matrix_world @ vert.co
                boundary_verts.append((vert.index, world_pos))
        
        bpy.ops.object.mode_set(mode='OBJECT')
        return boundary_verts
    
    def get_all_vertices_from_object(self, obj):
        """Get all vertices from a non-selectable object without entering edit mode"""
        vertices = []
        
        # Get mesh data directly without switching modes
        mesh = obj.data
        for i, vert in enumerate(mesh.vertices):
            # Convert to world coordinates
            world_pos = obj.matrix_world @ vert.co
            vertices.append((i, world_pos))
            
        return vertices
    
    def get_all_fixed_vertices(self):
        """Get all vertices from all fixed objects"""
        all_fixed_vertices = []
        
        for fixed_obj in self.fixed_objects:
            vertices = self.get_all_vertices_from_object(fixed_obj)
            # Add object reference to each vertex
            for idx, pos in vertices:
                all_fixed_vertices.append((fixed_obj.name, idx, pos))
                
        return all_fixed_vertices
    
    def find_closest_vertices(self, movable_boundary, all_fixed_vertices):
        """Find the closest vertex pairs between movable and all fixed vertices"""
        if not all_fixed_vertices:
            return []
            
        # Build KD-tree for all fixed vertices
        kd = kdtree.KDTree(len(all_fixed_vertices))
        for i, (obj_name, idx, pos) in enumerate(all_fixed_vertices):
            kd.insert(pos, i)
        kd.balance()
        
        connections = []
        for mov_idx, mov_pos in movable_boundary:
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
    
    def connect_vertices(self, connections):
        """Move movable vertices to connect with fixed vertices"""
        # Enter edit mode for movable object
        bpy.context.view_layer.objects.active = self.movable_obj
        bpy.ops.object.mode_set(mode='EDIT')
        
        bm = bmesh.from_edit_mesh(self.movable_obj.data)
        bm.verts.ensure_lookup_table()
        
        # Move vertices
        for connection in connections:
            mov_idx = connection['movable_idx']
            fixed_world_pos = connection['fixed_pos']
            
            # Convert world position to local coordinates of movable object
            local_pos = self.movable_obj.matrix_world.inverted() @ fixed_world_pos
            bm.verts[mov_idx].co = local_pos
        
        # Update mesh
        bmesh.update_edit_mesh(self.movable_obj.data)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        return len(connections)
    
    def dissolve_stray_vertices(self):
        """Dissolve vertices using limited dissolve to clean up geometry"""
        bpy.context.view_layer.objects.active = self.movable_obj
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Select all vertices
        bpy.ops.mesh.select_all(action='SELECT')
        
        # Use limited dissolve to clean up geometry while preserving shape
        bpy.ops.mesh.dissolve_limited(angle_limit=0.0174533, use_dissolve_boundaries=False)
        
        # Dissolve loose vertices instead of deleting them
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_loose()
        bpy.ops.mesh.dissolve_verts()
        
        bpy.ops.object.mode_set(mode='OBJECT')

class MESH_OT_connect_lod_vertices(Operator):
    """Connect LOD vertices automatically to body mesh"""
    bl_idname = "mesh.connect_lod_vertices"
    bl_label = "Connect LOD Vertices"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Configuration
        connection_threshold = 0.1
        
        # Find s4studio_ prefixed object
        movable_obj = None
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        for obj in selected_objects:
            if obj.name.startswith("s4studio_"):
                movable_obj = obj
                break
        
        # If no selected s4studio_ object, check active object
        if not movable_obj and context.active_object:
            if context.active_object.name.startswith("s4studio_"):
                movable_obj = context.active_object
        
        if not movable_obj:
            bpy.context.window_manager.popup_menu(display_popup_list([no_s4studio_mesh_found]), title="Creator Tools", icon='ERROR')
            return {'CANCELLED'}
        
        # Create connector and process
        connector = LODVertexConnector(movable_obj, connection_threshold)
        
        if not connector.fixed_objects:
            bpy.context.window_manager.popup_menu(display_popup_list([no_fixed_objects_found]), title="Creator Tools", icon='ERROR')
            return {'CANCELLED'}
        
        try:
            # Get boundary vertices from movable object
            movable_boundary = connector.get_boundary_vertices(movable_obj)
            
            # Get all vertices from fixed objects
            all_fixed_vertices = connector.get_all_fixed_vertices()
            
            # Find connections
            connections = connector.find_closest_vertices(movable_boundary, all_fixed_vertices)
            
            if not connections:
                bpy.context.window_manager.popup_menu(display_popup_list([no_connections_found]), title="Creator Tools", icon='ERROR')
                return {'CANCELLED'}
            
            # Connect vertices
            connected_count = connector.connect_vertices(connections)
            
            # Dissolve stray vertices
            connector.dissolve_stray_vertices()
            
            # Show success popup
            bpy.context.window_manager.popup_menu(display_popup_list([lambda s, c: vertex_connection_success(s, c, connected_count, movable_obj.name, connector.fixed_objects)]), title="Creator Tools", icon='MESH_DATA')
            
        except Exception as e:
            bpy.context.window_manager.popup_menu(display_popup_list([lambda s, c: vertex_connection_error(s, c, str(e))]), title="Creator Tools", icon='ERROR')
            return {'CANCELLED'}
        
        return {'FINISHED'}

def no_s4studio_mesh_found(self, context):
    self.layout.label(text="S4studio mesh not found.")

def no_fixed_objects_found(self, context):
    self.layout.label(text="No fixed body objects found in scene. Looking for objects named: bottom, feet, head and top")

def no_connections_found(self, context):
    self.layout.label(text="No vertices found within connection distance. Move vertices closer.")

def vertex_connection_success(self, context, connected_count, mesh_name, fixed_objects):
    self.layout.label(text=f"{mesh_name} connected to {', '.join([obj.name for obj in fixed_objects])}. {connected_count} vertices connected.")

def vertex_connection_error(self, context, error_message):
    self.layout.label(text="Error trying to connect vertices:")
    self.layout.label(text=error_message)

def display_popup_list(popups):
    def draw(self, context):
        layout = self.layout
        for popup in popups:
            popup(self, context)
    return draw

def register():
    bpy.utils.register_class(MESH_OT_connect_lod_vertices)

def unregister():
    bpy.utils.unregister_class(MESH_OT_connect_lod_vertices)

if __name__ == "__main__":
    register()