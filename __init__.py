import bpy
import os

# Add custom Imports Here
from . import si_uvchecker
from . import pi_prereq
from . import pi_bone_shape_destroyer
from . import pi_vertex_paint
from . import pi_weights
from . import pi_base_loader
from . import pi_rig_loader
from . import pi_rig_link
from . import pi_mesh
from . import pi_cutnum
from . import pi_datatransfer
from . import pi_wiresnap   
from . import lodeci

# Blender Addon Info
bl_info = {
    "name": "TS4 Creator Tools",
    "author": "CUUPIDON",
    "version": (1, 6),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > TS4 Creator Tools",
    "description": "Tools to take tedium out of the work flow.",
    "category": "Object",
}

# Addon Panel Info
class CUUPID_PT_creator_tools(bpy.types.Panel):
    bl_label = "TS4 Creator Tools"
    bl_idname = "CUUPID_PT_creator_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'TS4 Creator Tools'

    # Addon Buttons & Spaces
    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.label(icon='INFO')
        row.label(text="Tools to take tedium out of the work flow.")

        # Asset Importer
        assetimport_menu = layout.box().column()
        assetimport_menu.label(text="Asset Importer", icon='MESH_MONKEY')
        assetimport_menu.operator("object.load_body_base", text="Load Body Base...")
        assetimport_menu.operator("object.load_rig", text="Load Rig...")
        
        # Prerequisites 
        prerequisites_menu = layout.box().column()
        prerequisites_menu.label(text="Prerequisites", icon='CHECKBOX_HLT')
        prerequisites_menu.operator("object.resfs", text="Rename Mesh: S4S")
        prerequisites_menu.operator("object.reref", text="Rename Mesh: REF")

        # Mesh
        mesh_menu = layout.box().column()
        mesh_menu.label(text="Mesh", icon='OUTLINER_OB_MESH')
        mesh_menu.operator("object.rdmbd", text="Merge by Distance")
        mesh_menu.operator("object.sii_subdivision", text="Subdivide REF Mesh")
        mesh_menu.operator("object.delete_ref_mesh", text="Delete REF Mesh")
        mesh_menu.operator("object.s4studio_set_cut_number", text="Set Cut Number (NEED S4S)")
        mesh_menu.operator("object.quadfa", text="Tris To Quads")
        mesh_menu.operator("object.trifa", text="Triangulate Faces")

        # Main
        main_menu = layout.box().column()
        main_menu.label(text="UVs", icon='UV')
        main_menu.operator("object.si_uvchecker", text="UV Checker")
        main_menu.operator("object.siii_datatrans", text="Data Transfer")

        # Weights
        weights_menu = layout.box().column()
        weights_menu.label(text="Weights", icon='MOD_VERTEX_WEIGHT')
        weights_menu.operator("object.linkrig", text="Link Rig") 
        weights_menu.operator("object.siiii_weights", text="Weight Transfer")
        weights_menu.operator("object.smoothwe", text="Smooth Weights")
        weights_menu.operator("object.limwe", text="Limit Weights")
        
        # LOD Creation
        lod_menu = layout.box().column()
        lod_menu.label(text="LOD Creation", icon='SNAP_VERTEX')
        lod_menu.operator("mesh.generate_lod_levels", text="Generate LOD Levels")
        lod_menu.operator("mesh.setup_wireframe_snap", text="Wireframe Mode")

        # Vertex Paints
        vertex_paints_menu = layout.box().column()
        vertex_paints_menu.label(text="Vertex Paints", icon='VPAINT_HLT')
        vertex_paints_menu.operator("object.vtc_skintight", text="Skin Tight")
        vertex_paints_menu.operator("object.vtc_robemorph", text="Robe Morph")
        vertex_paints_menu.operator("object.vtc_hairline", text="Hairline")
        vertex_paints_menu.operator("object.vtc_hairacc", text="Hair Acc")
        vertex_paints_menu.operator("object.vtc_black", text="Black/NONE")
        vertex_paints_menu.operator("object.vtc_white", text="White/Lamp Glow")

# Register And Unregister
def register():
    bpy.utils.register_class(CUUPID_PT_creator_tools)
    si_uvchecker.register()
    pi_vertex_paint.register()
    pi_prereq.register()
    pi_base_loader.register()
    pi_rig_loader.register()
    pi_weights.register()
    pi_rig_link.register()
    pi_mesh.register()
    pi_cutnum.register()
    pi_datatransfer.register()
    pi_bone_shape_destroyer.register()
    pi_wiresnap.register()
    lodeci.register()
def unregister():
    bpy.utils.unregister_class(CUUPID_PT_creator_tools)
    si_uvchecker.unregister()
    pi_mesh.unregister()
    pi_vertex_paint.unregister()
    pi_base_loader.unregister()
    pi_rig_loader.unregister()
    pi_weights.unregister()
    pi_cutnum.unregister()
    pi_rig_link.unregister()
    pi_datatransfer.unregister()
    pi_bone_shape_destroyer.unregister()
    pi_wiresnap.unregister()
    lodeci.unregister()
# Only register when running as addon
if __name__ == "__main__":
    register()

# Popup Functions
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