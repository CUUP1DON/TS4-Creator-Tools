import bpy

# Popup message functions
def select_obj(self, context):
    self.layout.label(text="Please select or unhide your object.")

def exit_edit(self, context):
    self.layout.label(text="Exit Edit Mode first.")

def sfs_not_found(self, context):
    self.layout.label(text="s4studio_mesh_1 not found.")

def ref_not_found(self, context):
    self.layout.label(text="REF not found.")

def no_weight_groups(self, context):
    self.layout.label(text="Object you're trying to transfer from has no weight groups!")

def weight_trans(self, context):
    self.layout.label(text="Weights transferred. REF mesh removed.")

def sub_succ(self, context):
    self.layout.label(text="REF subdivided.")

def wesmo(self, context):
    self.layout.label(text="Weights smoothed.")

def wesmonog(self, context):
    self.layout.label(text="No weight groups.")

def limwesucc(self, context):
    self.layout.label(text="Number of weights per vertex limited.")

def rbmbdsucc(self, context):
    self.layout.label(text="Removed doubles.")

def ttqsucc(self, context):
    self.layout.label(text="Changed faces.")

def linkrigsucc(self, context):
    self.layout.label(text="Linked rig.")

def norig(self, context):
    self.layout.label(text="Cannot find rig, please make sure it is in your scene.")

# Helper function to display popup lists
def display_popup_list(popups):
    def draw_popup(self, context):
        for popup in popups:
            popup(self, context)
    return draw_popup

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
            popups = [select_obj]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
            return {'CANCELLED'}
        
        # Check if object is hidden
        if context.active_object.hide_get():
            popups = [select_obj]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
            return {'CANCELLED'}
        
        # Check if object is a mesh
        if context.active_object.type != 'MESH':
            popups = [lambda self, context: self.layout.label(text="Selected object is not a mesh.")]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
            return {'CANCELLED'}
        
        bpy.ops.object.mode_set(mode='EDIT')
        
        if context.active_object and context.active_object.mode == 'EDIT':
            obj = context.active_object
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles(threshold=self.threshold)
            
            popups = [rbmbdsucc]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='INFO')
        else:
            popups = [exit_edit]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
            return {'CANCELLED'}

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Merge by Distance", icon='AUTOMERGE_ON')
        layout.separator()
        
        col = layout.column(align=True)
        col.label(text="Merge Distance:")
        col.prop(self, "threshold", text="")
        
        layout.separator()
        row = layout.row()
        row.label(text="💡 Tip: Lower values merge fewer vertices", icon='INFO')

# Tris To Quads
class quadfa(bpy.types.Operator):
    bl_idname = "object.quadfa"
    bl_label = "Tris to Quads"
    bl_description = "Tris to Quads"

    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Tris to Quads")
        
        # Check if there's an active object
        if not context.active_object:
            popups = [select_obj]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
            return {'CANCELLED'}
        
        # Check if object is hidden
        if context.active_object.hide_get():
            popups = [select_obj]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
            return {'CANCELLED'}
        
        # Check if object is a mesh
        if context.active_object.type != 'MESH':
            popups = [lambda self, context: self.layout.label(text="Selected object is not a mesh.")]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
            return {'CANCELLED'}
        
        bpy.ops.object.mode_set(mode='EDIT')
        
        if context.active_object and context.active_object.mode == 'EDIT':
            obj = context.active_object
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.tris_convert_to_quads()
            
            popups = [ttqsucc]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='INFO')
        else:
            popups = [exit_edit]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
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
            popups = [select_obj]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
            return {'CANCELLED'}
        
        # Check if object is hidden
        if context.active_object.hide_get():
            popups = [select_obj]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
            return {'CANCELLED'}
        
        # Check if object is a mesh
        if context.active_object.type != 'MESH':
            popups = [lambda self, context: self.layout.label(text="Selected object is not a mesh.")]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
            return {'CANCELLED'}
        
        bpy.ops.object.mode_set(mode='EDIT')
        
        if context.active_object and context.active_object.mode == 'EDIT':
            obj = context.active_object
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')

            popups = [ttqsucc]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='INFO')
        else:
            popups = [exit_edit]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
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
                popups = [select_obj]
                bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
                return {'CANCELLED'}
        obj = bpy.data.objects.get("REF")
        if obj is None:
            popups = [ref_not_found]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
            return {'CANCELLED'}

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        modifier = obj.modifiers.new(name="Subdivision", type='SUBSURF')
        modifier.levels = self.levels
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        
        popups = [sub_succ]
        bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='INFO')
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