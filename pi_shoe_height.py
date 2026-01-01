import bpy
import bmesh
from bpy.types import Operator
from bpy.props import StringProperty
from . import pi_errors

class TSCT_OT_add_shoe_height_cut(Operator):
    bl_idname = "object.add_shoe_height_cut"
    bl_label = "Add Shoe Height Cut Plane"
    bl_description = "Add a plane for shoe height measurement at world origin"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Add Shoe Height Cut Plane")

        # Store the current mode and active object to restore later if needed
        original_mode = context.mode
        original_active = context.active_object

        # Switch to Object mode if not already in it
        if context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Set 3D cursor to world origin
        context.scene.cursor.location = (0.0, 0.0, 0.0)

        # Add a plane at cursor location
        bpy.ops.mesh.primitive_plane_add(
            size=1,
            location=(0.0, 0.0, 0.0),
            rotation=(0.0, 0.0, 0.0)
        )

        # Get the newly created plane
        plane = context.active_object

        # Scale it down to -0.000000001
        plane.scale = (-0.000000001, -0.000000001, -0.000000001)

        # Apply scale and rotation to transform (we're already in Object mode now)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

        # Rename the plane
        plane.name = "Auto Shoe Height Cut"

        # Restore the original active object and mode if needed
        if original_active and original_mode == 'EDIT_MESH':
            context.view_layer.objects.active = original_active
            original_active.select_set(True)
            bpy.ops.object.mode_set(mode='EDIT')

        self.report({'INFO'}, "Shoe Height Cut Plane added at world origin")
        return {'FINISHED'}


class TSCT_OT_rename_ash(Operator):
    bl_idname = "object.rename_ash"
    bl_label = "Rename Mesh: Add _ASH"
    bl_description = "Add _ASH suffix to selected mesh name for shoe height measurement"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Rename Mesh Add _ASH")

        # Check if there's an active object
        if not context.active_object:
            pi_errors.ErrorManager.show_error('no_object_selected')
            return {'CANCELLED'}

        obj = context.active_object

        # Check if it's a mesh
        if obj.type != 'MESH':
            pi_errors.ErrorManager.show_error('selected_not_mesh')
            return {'CANCELLED'}

        # Add _ASH suffix if not already present
        if not obj.name.endswith("_ASH"):
            obj.name = obj.name + "_ASH"
            pi_errors.ErrorManager.show_success('mesh_renamed', name=obj.name)
        else:
            pi_errors.ErrorManager.show_success('mesh_already_has_ash')

        return {'FINISHED'}


class TSCT_OT_find_ash_lowest(Operator):
    bl_idname = "object.find_ash_lowest"
    bl_label = "Calculate Z"
    bl_description = "Find mesh with _ASH suffix, select lowest face(s), and calculate Z coordinate"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Find ASH Lowest Face")

        # Find mesh with "_ASH" in name
        ash_mesh = None
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and '_ASH' in obj.name:
                ash_mesh = obj
                break

        if not ash_mesh:
            pi_errors.ErrorManager.show_error('no_ash_mesh_found')
            return {'CANCELLED'}

        # Make sure the object is visible and selectable
        if ash_mesh.hide_get():
            pi_errors.ErrorManager.show_error('ash_mesh_hidden')
            return {'CANCELLED'}

        # Check if we're already in edit mode with the _ASH mesh active
        already_in_edit_mode = (context.mode == 'EDIT_MESH' and
                                context.active_object == ash_mesh)

        if not already_in_edit_mode:
            # Select the mesh and make it active
            bpy.ops.object.select_all(action='DESELECT')
            ash_mesh.select_set(True)
            context.view_layer.objects.active = ash_mesh

            # Enter edit mode
            bpy.ops.object.mode_set(mode='EDIT')

        # Switch to face select mode
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')

        # Deselect all faces first
        bpy.ops.mesh.select_all(action='DESELECT')

        # Get BMesh data
        bm = bmesh.from_edit_mesh(ash_mesh.data)
        bm.faces.ensure_lookup_table()

        # Find the minimum Z coordinate among all face vertices
        min_z = float('inf')
        lowest_faces = []

        for face in bm.faces:
            # Get minimum Z of all vertices in this face
            face_min_z = min(vert.co.z for vert in face.verts)

            if face_min_z < min_z:
                min_z = face_min_z
                lowest_faces = [face]
            elif abs(face_min_z - min_z) < 0.0001:  # Tolerance for floating point comparison
                lowest_faces.append(face)

        # Select the lowest faces
        for face in lowest_faces:
            face.select = True

        # Update the mesh to show selection
        bmesh.update_edit_mesh(ash_mesh.data)

        # Store the Z value in scene property (formatted to 6 decimal places)
        context.scene.ash_lowest_z = f"{min_z:.6f}"

        # Show success message
        pi_errors.ErrorManager.show_success('ash_lowest_found', z_value=context.scene.ash_lowest_z)

        return {'FINISHED'}


class TSCT_OT_calculate_selected_z(Operator):
    bl_idname = "object.calculate_selected_z"
    bl_label = "Calculate Z from Selected Face"
    bl_description = "Calculate Z coordinate from currently selected face(s)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Calculate Z from Selected Face")

        # Check if we're in edit mode
        if context.mode != 'EDIT_MESH':
            pi_errors.ErrorManager.show_error('wrong_mode_edit_required')
            return {'CANCELLED'}

        # Check if active object is a mesh
        if not context.active_object or context.active_object.type != 'MESH':
            pi_errors.ErrorManager.show_error('selected_not_mesh')
            return {'CANCELLED'}

        ash_mesh = context.active_object

        # Get BMesh data
        bm = bmesh.from_edit_mesh(ash_mesh.data)

        # Get selected faces
        selected_faces = [f for f in bm.faces if f.select]

        if not selected_faces:
            pi_errors.ErrorManager.show_error('no_faces_selected')
            return {'CANCELLED'}

        # Calculate minimum Z from selected faces
        min_z = float('inf')
        for face in selected_faces:
            face_min_z = min(vert.co.z for vert in face.verts)
            if face_min_z < min_z:
                min_z = face_min_z

        # Store the Z value in scene property (formatted to 6 decimal places)
        context.scene.ash_lowest_z = f"{min_z:.6f}"

        # Show success message
        pi_errors.ErrorManager.show_success('ash_lowest_updated', z_value=context.scene.ash_lowest_z)

        return {'FINISHED'}


# Register and unregister functions
def register():
    bpy.utils.register_class(TSCT_OT_add_shoe_height_cut)
    bpy.utils.register_class(TSCT_OT_rename_ash)
    bpy.utils.register_class(TSCT_OT_find_ash_lowest)
    bpy.utils.register_class(TSCT_OT_calculate_selected_z)

    # Register Scene property for storing Z value
    bpy.types.Scene.ash_lowest_z = StringProperty(
        name="Lowest Z",
        description="Z coordinate of the lowest face of the _ASH mesh",
        default="Not calculated"
    )

def unregister():
    bpy.utils.unregister_class(TSCT_OT_add_shoe_height_cut)
    bpy.utils.unregister_class(TSCT_OT_rename_ash)
    bpy.utils.unregister_class(TSCT_OT_find_ash_lowest)
    bpy.utils.unregister_class(TSCT_OT_calculate_selected_z)

    # Unregister Scene property
    del bpy.types.Scene.ash_lowest_z
