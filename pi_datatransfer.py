import bpy
from bpy.props import EnumProperty
from . import pi_errors
from .ci_asset_management import show_popup

class siii_datatrans(bpy.types.Operator):
    bl_idname = "object.siii_datatrans"
    bl_label = "Data Transfer"
    bl_description = "Transfer UV data from REF mesh to your mesh"
    
    mapping_method: EnumProperty(
        name="Mapping Method",
        description="Choose the mapping method for UV transfer",
        items=[
            ('TOPOLOGY', 'Topology', 'Topology mapping'),
            ('NEAREST_NORMAL', 'Nearest Corner and Best Matching Normal', 'Nearest corner and best matching normal'),
            ('NEAREST_POLYNOR', 'Nearest Corner and Best Matching Face Normal', 'Nearest corner and best matching face normal'),
            ('NEAREST_POLY', 'Nearest Corner of Nearest Face', 'Nearest corner of nearest face'),
            ('POLYINTERP_NEAREST', 'Nearest Face Interpolated', 'Nearest face interpolated'),
            ('POLYINTERP_LNORPROJ', 'Projected Face Interpolated', 'Projected face interpolated')
        ],
        default='POLYINTERP_NEAREST'
    )
    
    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Data Transfer")
        
        obj_ref = bpy.data.objects.get("REF")
        obj_target = bpy.data.objects.get("s4studio_mesh_1")
        
        if not obj_ref:
            pi_errors.ErrorManager.show_error('file_not_found',
                custom_message="REF object not found",
                custom_details=["Load a REF object first",
                               "Make sure REF object is visible"])
            return {'CANCELLED'}
            
        if not obj_target:
            pi_errors.ErrorManager.show_error('file_not_found',
                custom_message="s4studio_mesh_1 object not found",
                custom_details=["Make sure S4Studio mesh is in your scene",
                               "Check object naming and visibility"])
            return {'CANCELLED'}
            
        if 'uv_1' not in obj_ref.data.uv_layers:
            pi_errors.ErrorManager.show_error('validation_error',
                custom_message="REF object missing UV map",
                custom_details=[
                    "REF does not have a uv_1 UV map",
                    "Run UV Checker on the REF object first",
                    "Make sure the REF has proper UV mapping"
                ])
            return {'CANCELLED'}
            
        if 'uv_1' not in obj_target.data.uv_layers:
            pi_errors.ErrorManager.show_error('validation_error',
                custom_message="S4Studio mesh missing UV map",
                custom_details=[
                    "s4studio_mesh_1 does not have a uv_1 UV map",
                    "Please run the UV Checker on your mesh first",
                    "This will create the required UV maps"
                ])
            return {'CANCELLED'}
        
        self.apply_data_transfer(obj_target, obj_ref)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        # Force the dialog to appear
        return context.window_manager.invoke_props_dialog(self)
    
    def display_popup_error(self, message):
        pi_errors.ErrorManager.show_error('validation_error', custom_message=message)
    
    def apply_data_transfer(self, obj_target, obj_ref):
        bpy.context.view_layer.objects.active = obj_target
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Check for topology mapping compatibility
        if self.mapping_method == 'TOPOLOGY':
            target_corners = len(obj_target.data.loops)
            ref_corners = len(obj_ref.data.loops)
            
            if target_corners != ref_corners:
                pi_errors.ErrorManager.show_error('topology_mismatch',
                    custom_message="Topology mapping requires identical mesh structure",
                    custom_details=[
                        f"Target mesh corners: {target_corners}",
                        f"REF mesh corners: {ref_corners}",
                        "",
                        "Solutions:",
                        "• Use a different mapping method",
                        "• Ensure both meshes have identical topology",
                        "• Try 'Nearest Face Interpolated' instead"
                    ])
                return
        
        bpy.ops.object.modifier_add(type='DATA_TRANSFER')
        
        mod = obj_target.modifiers[-1]
        mod.object = obj_ref
        mod.use_loop_data = True
        mod.data_types_loops = {'UV'}
        mod.loop_mapping = self.mapping_method  # Use the selected mapping method
        mod.layers_uv_select_src = 'uv_1'
        mod.layers_uv_select_dst = 'uv_1'
        
        bpy.ops.object.modifier_apply(modifier=mod.name)
        self.display_popup_success()
    
    def display_popup_success(self):
        pi_errors.ErrorManager.show_success('operation_complete',
            custom_message="UV data transfer completed!",
            custom_details=[
                "uv_1 data has been transferred from REF to your mesh",
            ])

def register():
    bpy.utils.register_class(siii_datatrans)

def unregister():
    bpy.utils.unregister_class(siii_datatrans)

# Legacy popup functions (kept for compatibility)
def select_obj(self, context):
    pi_errors.show_no_object_selected()

def exit_edit(self, context):
    pi_errors.show_exit_edit_mode()

def sfs_not_found(self, context):
    pi_errors.ErrorManager.show_error('file_not_found',
                                     custom_message="s4studio_mesh_1 not found.")

def ref_not_found(self, context):
    pi_errors.ErrorManager.show_error('file_not_found',
                                     custom_message="REF not found.")

def no_weight_groups(self, context):
    pi_errors.ErrorManager.show_error('no_weight_groups')

def weight_trans(self, context):
    pi_errors.ErrorManager.show_success('weights_transferred')

def sub_succ(self, context):
    pi_errors.ErrorManager.show_success('mesh_subdivided')

def wesmo(self, context):
    pi_errors.ErrorManager.show_success('weights_smoothed')

def wesmonog(self, context):
    pi_errors.ErrorManager.show_error('no_weight_groups')

def limwesucc(self, context):
    pi_errors.ErrorManager.show_success('weights_limited')

def rbmbdsucc(self, context):
    pi_errors.ErrorManager.show_success('doubles_removed')

def ttqsucc(self, context):
    pi_errors.ErrorManager.show_success('faces_converted')

def linkrigsucc(self, context):
    pi_errors.ErrorManager.show_success('rig_linked')

def norig(self, context):
    pi_errors.ErrorManager.show_error('no_rig_found')

def topology_error(self, context):
    pi_errors.ErrorManager.show_error('topology_mismatch')

if __name__ == "__main__":
    register()