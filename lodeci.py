import bpy
from bpy.types import Operator
from bpy.props import EnumProperty

class MESH_OT_generate_lod_levels(Operator):
    """Generate LOD levels from s4studio_mesh_1 object"""
    bl_idname = "mesh.generate_lod_levels"
    bl_label = "Generate LOD Levels"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Dropdown property for LOD selection
    lod_choice: EnumProperty(
        name="LOD Selection",
        description="Choose which LOD levels to generate",
        items=[
            ('1', "LOD 1", "Generate only LOD 1 at 75% decimation"),
            ('2', "LOD 2", "Generate only LOD 2 at 50% decimation"),
            ('3', "LOD 3", "Generate only LOD 3 at 25% decimation"),
            ('ALL', "All LODs", "Generate all LOD levels (1, 2, and 3)")
        ],
        default='ALL'
    )
    
    def invoke(self, context, event):
        # Force the dialog to appear
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        # Find the s4studio_mesh_1 object
        source_obj = bpy.data.objects.get("s4studio_mesh_1")
        
        if not source_obj:
            bpy.context.window_manager.popup_menu(display_popup_list([no_mesh_found]), title="Creator Tools", icon='ERROR')
            return {'CANCELLED'}
        
        # Create or get the single LOD collection
        collection_name = "LODs"
        if collection_name not in bpy.data.collections:
            lod_collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(lod_collection)
        else:
            lod_collection = bpy.data.collections[collection_name]
        
        # Decimation ratios for each LOD level
        decimation_data = {
            1: 0.75,  # LOD 1: 75%
            2: 0.5,   # LOD 2: 50%
            3: 0.25   # LOD 3: 25%
        }
        
        # Determine which LODs to create based on selection
        if self.lod_choice == 'ALL':
            lods_to_create = [1, 2, 3]
        else:
            lods_to_create = [int(self.lod_choice)]
        
        created_lods = []
        
        # Create selected LOD levels
        for lod_level in lods_to_create:
            ratio = decimation_data[lod_level]
            
            # Create a copy of the original mesh
            lod_obj = source_obj.copy()
            lod_obj.data = source_obj.data.copy()
            lod_obj.name = f"s4studio_mesh_1_LOD_{lod_level}"
            
            # Link to the single LOD collection
            lod_collection.objects.link(lod_obj)
            
            # Add decimate modifier
            decimate_mod = lod_obj.modifiers.new(name=f"Decimate_LOD_{lod_level}", type='DECIMATE')
            decimate_mod.decimate_type = 'COLLAPSE'
            decimate_mod.ratio = ratio
            
            # Apply the modifier
            bpy.context.view_layer.objects.active = lod_obj
            bpy.ops.object.modifier_apply(modifier=decimate_mod.name)
            
            created_lods.append(lod_level)
        
        # Show success popup with created LODs info
        bpy.context.window_manager.popup_menu(display_popup_list([lambda s, c: lod_success(s, c, created_lods)]), title="Creator Tools", icon='MESH_DATA')
        
        return {'FINISHED'}

def no_mesh_found(self, context):
    self.layout.label(text="Cannot find s4studio_mesh_1 object in scene.")

def lod_success(self, context, created_lods):
    self.layout.label(text="LOD levels generated successfully!")
    self.layout.label(text="All LODs placed in 'LOD Collection'")
    
    # Show info for each created LOD
    decimation_info = {1: "75%", 2: "50%", 3: "25%"}
    for lod in created_lods:
        self.layout.label(text=f"LOD {lod}: Decimated to {decimation_info[lod]}")

def display_popup_list(popups):
    def draw(self, context):
        layout = self.layout
        for popup in popups:
            popup(self, context)
    return draw

def register():
    bpy.utils.register_class(MESH_OT_generate_lod_levels)

def unregister():
    bpy.utils.unregister_class(MESH_OT_generate_lod_levels)

if __name__ == "__main__":
    register()