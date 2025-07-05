import bpy
from bpy.types import Operator

class MESH_OT_generate_lod_levels(Operator):
    """Generate LOD levels from s4studio_mesh_1 object"""
    bl_idname = "mesh.generate_lod_levels"
    bl_label = "Generate LOD Levels"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Find the s4studio_mesh_1 object
        source_obj = bpy.data.objects.get("s4studio_mesh_1")
        
        if not source_obj:
            bpy.context.window_manager.popup_menu(display_popup_list([no_mesh_found]), title="Creator Tools", icon='ERROR')
            return {'CANCELLED'}
        
        # Create collections for each LOD level
        lod_collections = {}
        for i in range(1, 4):  # LOD 1, LOD 2, LOD 3
            collection_name = f"LOD {i}"
            if collection_name not in bpy.data.collections:
                new_collection = bpy.data.collections.new(collection_name)
                bpy.context.scene.collection.children.link(new_collection)
            lod_collections[i] = bpy.data.collections[collection_name]
        
        # Decimation ratios for each LOD level
        decimation_ratios = [0.75, 0.5, 0.25]  # LOD 1: 75%, LOD 2: 50%, LOD 3: 25%
        
        # Create decimated versions
        for i, ratio in enumerate(decimation_ratios, 1):
            # Create a copy of the original mesh
            lod_obj = source_obj.copy()
            lod_obj.data = source_obj.data.copy()
            lod_obj.name = f"s4studio_mesh_1_LOD {i}"
            
            # Link to appropriate collection
            lod_collections[i].objects.link(lod_obj)
            
            # Add decimate modifier
            decimate_mod = lod_obj.modifiers.new(name=f"Decimate_LOD {i}", type='DECIMATE')
            decimate_mod.decimate_type = 'COLLAPSE'
            decimate_mod.ratio = ratio
            
            # Apply the modifier
            bpy.context.view_layer.objects.active = lod_obj
            bpy.ops.object.modifier_apply(modifier=decimate_mod.name)
        
        # Show success popup
        bpy.context.window_manager.popup_menu(display_popup_list([lod_success]), title="Creator Tools", icon='MESH_DATA')
        
        return {'FINISHED'}

def no_mesh_found(self, context):
    self.layout.label(text="Cannot find s4studio_mesh_1 object in scene.")

def lod_success(self, context):
    self.layout.label(text="LOD levels generated successfully!")
    self.layout.label(text="LOD 1: Decimated to 75%")
    self.layout.label(text="LOD 2: Decimated to 50%")
    self.layout.label(text="LOD 3: Decimated to 25%")

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