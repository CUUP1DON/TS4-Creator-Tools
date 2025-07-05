import bpy

# Vertex Colors
class vtc_skintight(bpy.types.Operator):
    bl_idname = "object.vtc_skintight"
    bl_label = "Skin Tight"
    bl_description = "Give your mesh the Skin Tight vertex color"

    def execute(self, context):
        obj = context.active_object
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "No active mesh object selected")
            return {'CANCELLED'}

        self.vtc_skintight(context, obj)
        return {'FINISHED'}

    def vtc_skintight(self, context, obj):
        bpy.ops.ed.undo_push(message="Creator Tools: Vertex Color: ST")
        
        def display_vertex_success(self, context):
            self.layout.label(text="Changed vertex color to Skin Tight.")
        
        def display_vertex_failure(self, context):
            self.layout.label(text="Cannot find active mesh object.")

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
            bpy.context.window_manager.popup_menu(display_vertex_success, title="Creator Tools", icon='INFO')
        else:
            bpy.context.window_manager.popup_menu(display_vertex_failure, title="Creator Tools", icon='ERROR')

class vtc_robemorph(bpy.types.Operator):
    bl_idname = "object.vtc_robemorph"
    bl_label = "Robe Morph"
    bl_description = "Give your mesh the Robe Morph vertex color"

    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Vertex Color: RM")
        obj = context.active_object
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "No active mesh object selected")
            return {'CANCELLED'}

        self.vtc_robemorph(context, obj)
        return {'FINISHED'}

    def vtc_robemorph(self, context, obj):
        def display_vertex_success(self, context):
            self.layout.label(text="Changed vertex color to Robe Morph.")
        
        def display_vertex_failure(self, context):
            self.layout.label(text="Cannot find active mesh object.")

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
            bpy.context.window_manager.popup_menu(display_vertex_success, title="Creator Tools", icon='INFO')
        else:
            bpy.context.window_manager.popup_menu(display_vertex_failure, title="Creator Tools", icon='ERROR')

class vtc_hairline(bpy.types.Operator):
    bl_idname = "object.vtc_hairline"
    bl_label = "Hairline"
    bl_description = "Give your mesh the Hairline vertex color"

    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Vertex Color: HL")
        obj = context.active_object
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "No active mesh object selected")
            return {'CANCELLED'}

        self.vtc_hairline(context, obj)
        return {'FINISHED'}

    def vtc_hairline(self, context, obj):
        def display_vertex_success(self, context):
            self.layout.label(text="Changed vertex color to Hairline.")
        
        def display_vertex_failure(self, context):
            self.layout.label(text="Cannot find active mesh object.")

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
            bpy.context.window_manager.popup_menu(display_vertex_success, title="Creator Tools", icon='INFO')
        else:
            bpy.context.window_manager.popup_menu(display_vertex_failure, title="Creator Tools", icon='ERROR')

class vtc_hairacc(bpy.types.Operator):
    bl_idname = "object.vtc_hairacc"
    bl_label = "Hair Acc"
    bl_description = "Give your mesh the Hair Acc vertex color"

    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Vertex Color: HA")
        obj = context.active_object
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "No active mesh object selected")
            return {'CANCELLED'}

        self.vtc_hairacc(context, obj)
        return {'FINISHED'}

    def vtc_hairacc(self, context, obj):
        def display_vertex_success(self, context):
            self.layout.label(text="Changed vertex color to Hair Acc.")
        
        def display_vertex_failure(self, context):
            self.layout.label(text="Cannot find active mesh object.")

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
            bpy.context.window_manager.popup_menu(display_vertex_success, title="Creator Tools", icon='INFO')
        else:
            bpy.context.window_manager.popup_menu(display_vertex_failure, title="Creator Tools", icon='ERROR')

class vtc_black(bpy.types.Operator):
    bl_idname = "object.vtc_black"
    bl_label = "Black/NONE"
    bl_description = "Give your mesh the black vertex color"

    def execute(self, context):
        obj = context.active_object
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "No active mesh object selected")
            return {'CANCELLED'}

        self.vtc_skintight(context, obj)
        return {'FINISHED'}

    def vtc_skintight(self, context, obj):
        bpy.ops.ed.undo_push(message="Creator Tools: Vertex Color: Black")
        
        def display_vertex_success(self, context):
            self.layout.label(text="Changed vertex color to black.")
        
        def display_vertex_failure(self, context):
            self.layout.label(text="Cannot find active mesh object.")

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
            bpy.context.window_manager.popup_menu(display_vertex_success, title="Creator Tools", icon='INFO')
        else:
            bpy.context.window_manager.popup_menu(display_vertex_failure, title="Creator Tools", icon='ERROR')

class vtc_white(bpy.types.Operator):
    bl_idname = "object.vtc_white"
    bl_label = "White/Lamp Glow"
    bl_description = "Give your mesh the white vertex color"

    def execute(self, context):
        obj = context.active_object
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "No active mesh object selected")
            return {'CANCELLED'}

        self.vtc_skintight(context, obj)
        return {'FINISHED'}

    def vtc_skintight(self, context, obj):
        bpy.ops.ed.undo_push(message="Creator Tools: Vertex Color: White")
        
        def display_vertex_success(self, context):
            self.layout.label(text="Changed vertex color to white.")
        
        def display_vertex_failure(self, context):
            self.layout.label(text="Cannot find active mesh object.")

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