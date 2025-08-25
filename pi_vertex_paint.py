import bpy

# Vertex Colors
class vtc_skintight(bpy.types.Operator):
    bl_idname = "object.vtc_skintight"
    bl_label = "Skin Tight"
    bl_description = "Give your mesh the Skin Tight vertex color"

    def execute(self, context):
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not selected_objects:
            self.report({'ERROR'}, "No mesh objects selected")
            return {'CANCELLED'}

        self.vtc_skintight(context, selected_objects)
        return {'FINISHED'}

    def vtc_skintight(self, context, objects):
        bpy.ops.ed.undo_push(message="Creator Tools: Vertex Color: ST")
        
        def display_vertex_success(self, context):
            self.layout.label(text=f"Changed vertex color to Skin Tight on {len(objects)} object(s).")
        
        def display_vertex_failure(self, context):
            self.layout.label(text="Cannot find mesh objects.")

        success_count = 0
        for obj in objects:
            if obj is not None and obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='VERTEX_PAINT')
                if obj.data.vertex_colors:
                    vcol_layer = obj.data.vertex_colors.active
                else:
                    vcol_layer = obj.data.vertex_colors.new()
                for poly in obj.data.polygons:
                    for loop_index in poly.loop_indices:
                        vcol_layer.data[loop_index].color = (0.0, 1.0, 0.0, 1.0)
                success_count += 1
        
        if success_count > 0:
            bpy.context.window_manager.popup_menu(display_vertex_success, title="Creator Tools", icon='INFO')
        else:
            bpy.context.window_manager.popup_menu(display_vertex_failure, title="Creator Tools", icon='ERROR')

class vtc_robemorph(bpy.types.Operator):
    bl_idname = "object.vtc_robemorph"
    bl_label = "Robe Morph"
    bl_description = "Give your mesh the Robe Morph vertex color"

    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Vertex Color: RM")
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not selected_objects:
            self.report({'ERROR'}, "No mesh objects selected")
            return {'CANCELLED'}

        self.vtc_robemorph(context, selected_objects)
        return {'FINISHED'}

    def vtc_robemorph(self, context, objects):
        def display_vertex_success(self, context):
            self.layout.label(text=f"Changed vertex color to Robe Morph on {len(objects)} object(s).")
        
        def display_vertex_failure(self, context):
            self.layout.label(text="Cannot find mesh objects.")

        success_count = 0
        for obj in objects:
            if obj is not None and obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='VERTEX_PAINT')
                if obj.data.vertex_colors:
                    vcol_layer = obj.data.vertex_colors.active
                else:
                    vcol_layer = obj.data.vertex_colors.new()
                    
                for poly in obj.data.polygons:
                    for loop_index in poly.loop_indices:
                        vcol_layer.data[loop_index].color = (0.247059, 0.941177, 0.0, 1.0)
                success_count += 1
        
        if success_count > 0:
            bpy.context.window_manager.popup_menu(display_vertex_success, title="Creator Tools", icon='INFO')
        else:
            bpy.context.window_manager.popup_menu(display_vertex_failure, title="Creator Tools", icon='ERROR')

class vtc_hairline(bpy.types.Operator):
    bl_idname = "object.vtc_hairline"
    bl_label = "Hairline"
    bl_description = "Give your mesh the Hairline vertex color"

    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Vertex Color: HL")
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not selected_objects:
            self.report({'ERROR'}, "No mesh objects selected")
            return {'CANCELLED'}

        self.vtc_hairline(context, selected_objects)
        return {'FINISHED'}

    def vtc_hairline(self, context, objects):
        def display_vertex_success(self, context):
            self.layout.label(text=f"Changed vertex color to Hairline on {len(objects)} object(s).")
        
        def display_vertex_failure(self, context):
            self.layout.label(text="Cannot find mesh objects.")

        success_count = 0
        for obj in objects:
            if obj is not None and obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='VERTEX_PAINT')
                if obj.data.vertex_colors:
                    vcol_layer = obj.data.vertex_colors.active
                else:
                    vcol_layer = obj.data.vertex_colors.new()
                    
                for poly in obj.data.polygons:
                    for loop_index in poly.loop_indices:
                        vcol_layer.data[loop_index].color = (0.0, 0.498039, 0.247059, 1.0)
                success_count += 1
        
        if success_count > 0:
            bpy.context.window_manager.popup_menu(display_vertex_success, title="Creator Tools", icon='INFO')
        else:
            bpy.context.window_manager.popup_menu(display_vertex_failure, title="Creator Tools", icon='ERROR')

class vtc_hairacc(bpy.types.Operator):
    bl_idname = "object.vtc_hairacc"
    bl_label = "Hair Acc"
    bl_description = "Give your mesh the Hair Acc vertex color"

    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Vertex Color: HA")
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not selected_objects:
            self.report({'ERROR'}, "No mesh objects selected")
            return {'CANCELLED'}

        self.vtc_hairacc(context, selected_objects)
        return {'FINISHED'}

    def vtc_hairacc(self, context, objects):
        def display_vertex_success(self, context):
            self.layout.label(text=f"Changed vertex color to Hair Acc on {len(objects)} object(s).")
        
        def display_vertex_failure(self, context):
            self.layout.label(text="Cannot find mesh objects.")

        success_count = 0
        for obj in objects:
            if obj is not None and obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='VERTEX_PAINT')
                if obj.data.vertex_colors:
                    vcol_layer = obj.data.vertex_colors.active
                else:
                    vcol_layer = obj.data.vertex_colors.new()
                    
                for poly in obj.data.polygons:
                    for loop_index in poly.loop_indices:
                        vcol_layer.data[loop_index].color = (0.0, 0.498039, 0.0, 1.0)
                success_count += 1
        
        if success_count > 0:
            bpy.context.window_manager.popup_menu(display_vertex_success, title="Creator Tools", icon='INFO')
        else:
            bpy.context.window_manager.popup_menu(display_vertex_failure, title="Creator Tools", icon='ERROR')

class vtc_black(bpy.types.Operator):
    bl_idname = "object.vtc_black"
    bl_label = "Black/NONE"
    bl_description = "Give your mesh the black vertex color"

    def execute(self, context):
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not selected_objects:
            self.report({'ERROR'}, "No mesh objects selected")
            return {'CANCELLED'}

        self.vtc_black(context, selected_objects)
        return {'FINISHED'}

    def vtc_black(self, context, objects):
        bpy.ops.ed.undo_push(message="Creator Tools: Vertex Color: Black")
        
        def display_vertex_success(self, context):
            self.layout.label(text=f"Changed vertex color to black on {len(objects)} object(s).")
        
        def display_vertex_failure(self, context):
            self.layout.label(text="Cannot find mesh objects.")

        success_count = 0
        for obj in objects:
            if obj is not None and obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='VERTEX_PAINT')
                if obj.data.vertex_colors:
                    vcol_layer = obj.data.vertex_colors.active
                else:
                    vcol_layer = obj.data.vertex_colors.new()
                for poly in obj.data.polygons:
                    for loop_index in poly.loop_indices:
                        vcol_layer.data[loop_index].color = (0.0, 0.0, 0.0, 0.0)
                success_count += 1
        
        if success_count > 0:
            bpy.context.window_manager.popup_menu(display_vertex_success, title="Creator Tools", icon='INFO')
        else:
            bpy.context.window_manager.popup_menu(display_vertex_failure, title="Creator Tools", icon='ERROR')

class vtc_white(bpy.types.Operator):
    bl_idname = "object.vtc_white"
    bl_label = "White/Lamp Glow"
    bl_description = "Give your mesh the white vertex color"

    def execute(self, context):
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not selected_objects:
            self.report({'ERROR'}, "No mesh objects selected")
            return {'CANCELLED'}

        self.vtc_white(context, selected_objects)
        return {'FINISHED'}

    def vtc_white(self, context, objects):
        bpy.ops.ed.undo_push(message="Creator Tools: Vertex Color: White")
        
        def display_vertex_success(self, context):
            self.layout.label(text=f"Changed vertex color to white on {len(objects)} object(s).")
        
        def display_vertex_failure(self, context):
            self.layout.label(text="Cannot find mesh objects.")

        success_count = 0
        for obj in objects:
            if obj is not None and obj.type == 'MESH':
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='VERTEX_PAINT')
                if obj.data.vertex_colors:
                    vcol_layer = obj.data.vertex_colors.active
                else:
                    vcol_layer = obj.data.vertex_colors.new()
                for poly in obj.data.polygons:
                    for loop_index in poly.loop_indices:
                        vcol_layer.data[loop_index].color = (1.0, 1.0, 1.0, 1.0)
                success_count += 1
        
        if success_count > 0:
            bpy.context.window_manager.popup_menu(display_vertex_success, title="Creator Tools", icon='INFO')
        else:
            bpy.context.window_manager.popup_menu(display_vertex_failure, title="Creator Tools", icon='ERROR')

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