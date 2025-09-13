import bpy
from . import pi_errors

# Vertex Colors
class vtc_skintight(bpy.types.Operator):
    bl_idname = "object.vtc_skintight"
    bl_label = "Skin Tight"
    bl_description = "Give your mesh the Skin Tight vertex color"

    def execute(self, context):
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not selected_objects:
            pi_errors.show_no_mesh_selected()
            return {'CANCELLED'}

        self.vtc_skintight(context, selected_objects)
        return {'FINISHED'}

    def vtc_skintight(self, context, objects):
        bpy.ops.ed.undo_push(message="Creator Tools: Vertex Color: ST")

        success_count = 0
        for obj in objects:
            if obj is not None and obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='VERTEX_PAINT')
                if obj.data.vertex_colors:
                    vcol_layer = obj.data.vertex_colors.active
                else:
                    vcol_layer = obj.data.vertex_colors.new()
                # Check if paint mask or vertex selection mode is active
                mesh = obj.data
                use_paint_mask = mesh.use_paint_mask
                use_paint_mask_vertex = mesh.use_paint_mask_vertex
                
                for poly in mesh.polygons:
                    # Skip if paint mask is enabled and face is not selected
                    if use_paint_mask and not poly.select:
                        continue
                        
                    for loop_index in poly.loop_indices:
                        # Skip if vertex selection mask is enabled and vertex is not selected
                        if use_paint_mask_vertex:
                            vertex_index = mesh.loops[loop_index].vertex_index
                            if not mesh.vertices[vertex_index].select:
                                continue
                        
                        vcol_layer.data[loop_index].color = (0.0, 1.0, 0.0, 1.0)
                success_count += 1
        
        if success_count > 0:
            pi_errors.show_vertex_color_applied(count=success_count, color_type="Skin Tight")
        else:
            pi_errors.show_no_mesh_selected()

class vtc_robemorph(bpy.types.Operator):
    bl_idname = "object.vtc_robemorph"
    bl_label = "Robe Morph"
    bl_description = "Give your mesh the Robe Morph vertex color"

    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Vertex Color: RM")
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not selected_objects:
            pi_errors.show_no_mesh_selected()
            return {'CANCELLED'}

        self.vtc_robemorph(context, selected_objects)
        return {'FINISHED'}

    def vtc_robemorph(self, context, objects):
        success_count = 0
        for obj in objects:
            if obj is not None and obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='VERTEX_PAINT')
                if obj.data.vertex_colors:
                    vcol_layer = obj.data.vertex_colors.active
                else:
                    vcol_layer = obj.data.vertex_colors.new()
                    
                # Check if paint mask or vertex selection mode is active
                mesh = obj.data
                use_paint_mask = mesh.use_paint_mask
                use_paint_mask_vertex = mesh.use_paint_mask_vertex
                
                for poly in mesh.polygons:
                    # Skip if paint mask is enabled and face is not selected
                    if use_paint_mask and not poly.select:
                        continue
                        
                    for loop_index in poly.loop_indices:
                        # Skip if vertex selection mask is enabled and vertex is not selected
                        if use_paint_mask_vertex:
                            vertex_index = mesh.loops[loop_index].vertex_index
                            if not mesh.vertices[vertex_index].select:
                                continue
                        
                        vcol_layer.data[loop_index].color = (0.247059, 0.941177, 0.0, 1.0)
                success_count += 1
        
        if success_count > 0:
            pi_errors.show_vertex_color_applied(count=success_count, color_type="Robe Morph")
        else:
            pi_errors.show_no_mesh_selected()

class vtc_hairline(bpy.types.Operator):
    bl_idname = "object.vtc_hairline"
    bl_label = "Hairline"
    bl_description = "Give your mesh the Hairline vertex color"

    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Vertex Color: HL")
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not selected_objects:
            pi_errors.show_no_mesh_selected()
            return {'CANCELLED'}

        self.vtc_hairline(context, selected_objects)
        return {'FINISHED'}

    def vtc_hairline(self, context, objects):
        success_count = 0
        for obj in objects:
            if obj is not None and obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='VERTEX_PAINT')
                if obj.data.vertex_colors:
                    vcol_layer = obj.data.vertex_colors.active
                else:
                    vcol_layer = obj.data.vertex_colors.new()
                    
                # Check if paint mask or vertex selection mode is active
                mesh = obj.data
                use_paint_mask = mesh.use_paint_mask
                use_paint_mask_vertex = mesh.use_paint_mask_vertex
                
                for poly in mesh.polygons:
                    # Skip if paint mask is enabled and face is not selected
                    if use_paint_mask and not poly.select:
                        continue
                        
                    for loop_index in poly.loop_indices:
                        # Skip if vertex selection mask is enabled and vertex is not selected
                        if use_paint_mask_vertex:
                            vertex_index = mesh.loops[loop_index].vertex_index
                            if not mesh.vertices[vertex_index].select:
                                continue
                        
                        vcol_layer.data[loop_index].color = (0.0, 0.498039, 0.247059, 1.0)
                success_count += 1
        
        if success_count > 0:
            pi_errors.show_vertex_color_applied(count=success_count, color_type="Hairline")
        else:
            pi_errors.show_no_mesh_selected()

class vtc_hairacc(bpy.types.Operator):
    bl_idname = "object.vtc_hairacc"
    bl_label = "Hair Acc"
    bl_description = "Give your mesh the Hair Acc vertex color"

    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Vertex Color: HA")
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not selected_objects:
            pi_errors.show_no_mesh_selected()
            return {'CANCELLED'}

        self.vtc_hairacc(context, selected_objects)
        return {'FINISHED'}

    def vtc_hairacc(self, context, objects):
        success_count = 0
        for obj in objects:
            if obj is not None and obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='VERTEX_PAINT')
                if obj.data.vertex_colors:
                    vcol_layer = obj.data.vertex_colors.active
                else:
                    vcol_layer = obj.data.vertex_colors.new()
                    
                # Check if paint mask or vertex selection mode is active
                mesh = obj.data
                use_paint_mask = mesh.use_paint_mask
                use_paint_mask_vertex = mesh.use_paint_mask_vertex
                
                for poly in mesh.polygons:
                    # Skip if paint mask is enabled and face is not selected
                    if use_paint_mask and not poly.select:
                        continue
                        
                    for loop_index in poly.loop_indices:
                        # Skip if vertex selection mask is enabled and vertex is not selected
                        if use_paint_mask_vertex:
                            vertex_index = mesh.loops[loop_index].vertex_index
                            if not mesh.vertices[vertex_index].select:
                                continue
                        
                        vcol_layer.data[loop_index].color = (0.0, 0.498039, 0.0, 1.0)
                success_count += 1
        
        if success_count > 0:
            pi_errors.show_vertex_color_applied(count=success_count, color_type="Hair Accessory")
        else:
            pi_errors.show_no_mesh_selected()

class vtc_black(bpy.types.Operator):
    bl_idname = "object.vtc_black"
    bl_label = "Black/NONE"
    bl_description = "Give your mesh the black vertex color"

    def execute(self, context):
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not selected_objects:
            pi_errors.show_no_mesh_selected()
            return {'CANCELLED'}

        self.vtc_black(context, selected_objects)
        return {'FINISHED'}

    def vtc_black(self, context, objects):
        bpy.ops.ed.undo_push(message="Creator Tools: Vertex Color: Black")

        success_count = 0
        for obj in objects:
            if obj is not None and obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='VERTEX_PAINT')
                if obj.data.vertex_colors:
                    vcol_layer = obj.data.vertex_colors.active
                else:
                    vcol_layer = obj.data.vertex_colors.new()
                # Check if paint mask or vertex selection mode is active
                mesh = obj.data
                use_paint_mask = mesh.use_paint_mask
                use_paint_mask_vertex = mesh.use_paint_mask_vertex
                
                for poly in mesh.polygons:
                    # Skip if paint mask is enabled and face is not selected
                    if use_paint_mask and not poly.select:
                        continue
                        
                    for loop_index in poly.loop_indices:
                        # Skip if vertex selection mask is enabled and vertex is not selected
                        if use_paint_mask_vertex:
                            vertex_index = mesh.loops[loop_index].vertex_index
                            if not mesh.vertices[vertex_index].select:
                                continue
                        
                        vcol_layer.data[loop_index].color = (0.0, 0.0, 0.0, 0.0)
                success_count += 1
        
        if success_count > 0:
            pi_errors.show_vertex_color_applied(count=success_count, color_type="Black/None")
        else:
            pi_errors.show_no_mesh_selected()

class vtc_white(bpy.types.Operator):
    bl_idname = "object.vtc_white"
    bl_label = "White/Lamp Glow"
    bl_description = "Give your mesh the white vertex color"

    def execute(self, context):
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not selected_objects:
            pi_errors.show_no_mesh_selected()
            return {'CANCELLED'}

        self.vtc_white(context, selected_objects)
        return {'FINISHED'}

    def vtc_white(self, context, objects):
        bpy.ops.ed.undo_push(message="Creator Tools: Vertex Color: White")

        success_count = 0
        for obj in objects:
            if obj is not None and obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='VERTEX_PAINT')
                if obj.data.vertex_colors:
                    vcol_layer = obj.data.vertex_colors.active
                else:
                    vcol_layer = obj.data.vertex_colors.new()
                # Check if paint mask or vertex selection mode is active
                mesh = obj.data
                use_paint_mask = mesh.use_paint_mask
                use_paint_mask_vertex = mesh.use_paint_mask_vertex
                
                for poly in mesh.polygons:
                    # Skip if paint mask is enabled and face is not selected
                    if use_paint_mask and not poly.select:
                        continue
                        
                    for loop_index in poly.loop_indices:
                        # Skip if vertex selection mask is enabled and vertex is not selected
                        if use_paint_mask_vertex:
                            vertex_index = mesh.loops[loop_index].vertex_index
                            if not mesh.vertices[vertex_index].select:
                                continue
                        
                        vcol_layer.data[loop_index].color = (1.0, 1.0, 1.0, 1.0)
                success_count += 1
        
        if success_count > 0:
            pi_errors.show_vertex_color_applied(count=success_count, color_type="White/Lamp Glow")
        else:
            pi_errors.show_no_mesh_selected()

# Registration
classes = [
    vtc_skintight,
    vtc_robemorph,
    vtc_hairline,
    vtc_hairacc,
    vtc_black,
    vtc_white,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()