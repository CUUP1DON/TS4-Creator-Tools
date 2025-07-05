import bpy


# Popups
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

def display_popup_list(popups):
    def draw(self, context):
        layout = self.layout
        for popup in popups:
            popup(self, context)
    return draw


class siii_datatrans(bpy.types.Operator):
    bl_idname = "object.siii_datatrans"
    bl_label = "Data Transfer"
    bl_description = "Transfer UV data from REF mesh to your mesh"
    
    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Data Transfer")
        
        obj_ref = bpy.data.objects.get("REF")
        obj_target = bpy.data.objects.get("s4studio_mesh_1")
        
        if not obj_ref:
            popups = [ref_not_found]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
            return {'CANCELLED'}
           
        if not obj_target:
            popups = [sfs_not_found]
            bpy.context.window_manager.popup_menu(display_popup_list(popups), title="Creator Tools", icon='ERROR')
            return {'CANCELLED'}
            
        if 'uv_1' not in obj_ref.data.uv_layers:
            self.display_popup_error("REF does not have a uv_1.")
            return {'CANCELLED'}
            
        if 'uv_1' not in obj_target.data.uv_layers:
            self.display_popup_error("s4studio_mesh_1 does not have a uv_1 UV map. Please run the UV checker!")
            return {'CANCELLED'}
            
        self.apply_data_transfer(obj_target, obj_ref)
        return {'FINISHED'}
    
    def display_popup_error(self, message):
        def popup(self, context):
            self.layout.label(text=message)
        bpy.context.window_manager.popup_menu(popup, title="Creator Tools", icon='ERROR')
    
    def apply_data_transfer(self, obj_target, obj_ref):
        bpy.context.view_layer.objects.active = obj_target
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.modifier_add(type='DATA_TRANSFER')
        
        mod = obj_target.modifiers[-1]
        mod.object = obj_ref
        mod.use_loop_data = True
        mod.data_types_loops = {'UV'}
        mod.loop_mapping = 'POLYINTERP_NEAREST'
        mod.layers_uv_select_src = 'uv_1'
        mod.layers_uv_select_dst = 'uv_1'
        
        bpy.ops.object.modifier_apply(modifier=mod.name)
        self.display_popup_success()
    
    def display_popup_success(self):
        def popup(self, context):
            self.layout.label(text="Good to go!")
        bpy.context.window_manager.popup_menu(popup, title="Creator Tools", icon='INFO')


def register():
    bpy.utils.register_class(siii_datatrans)


def unregister():
    bpy.utils.unregister_class(siii_datatrans)


if __name__ == "__main__":
    register()