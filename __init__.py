import bpy
import os

# Add custom Imports Here
from . import constants
from . import pi_errors
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
from . import pi_cas_loader
from . import pi_occult_loader
from . import pi_anim_loader
from . import pi_lodconnect
from . import pi_transparency
from . import pi_bakes
from . import pi_shoe_height
from . import user_preferences

#Custom Loader
from . import ci_asset_management
from . import ci_base_loader
from . import ci_animation_loader
from . import ci_body_loader
from . import ci_cas_loader
from . import ci_rig_loader


# Blender Addon Info
bl_info = {
    "name": "TS4 Creator Tools",
    "author": "CUUPIDON",
    "version": (2, 0, 0),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > TS4CT",
    "description": "Tools to take tedium out of the work flow.",
    "category": "Object",
}

# Addon Panel Info
class CUUPID_PT_creator_tools(bpy.types.Panel):
    bl_label = "TS4 Creator Tools"
    bl_idname = "CUUPID_PT_creator_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'TS4CT'

    # Addon Buttons & Spaces
    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.label(icon='INFO')
        row.label(text="Tools to take tedium out of the work flow.")

        # Asset Importer
        box = layout.box()
        row = box.row()
        row.prop(context.scene, "ts4ct_show_asset_importer", icon="TRIA_DOWN" if context.scene.ts4ct_show_asset_importer else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text="Asset Importer", icon='MESH_MONKEY')
        if context.scene.ts4ct_show_asset_importer:
            col = box.column()
            col.operator("object.load_body_base", text="Load Body Base...")
            col.operator("object.load_cas", text="Load CAS Items...")
            col.operator("object.load_occult", text="Load Occult Items...")

        # Anim Importer
        box = layout.box()
        row = box.row()
        row.prop(context.scene, "ts4ct_show_anim_importer", icon="TRIA_DOWN" if context.scene.ts4ct_show_anim_importer else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text="Anim Importer", icon='ARMATURE_DATA')
        if context.scene.ts4ct_show_anim_importer:
            col = box.column()
            col.operator("object.load_rig", text="Load Rig...")
            col.operator("object.linkrig", text="Link Rig")
            col.operator("object.load_anim", text="Load Animation...")
            col.operator("object.restore_anim", text="Clear Animation")

        # REF
        box = layout.box()
        row = box.row()
        row.prop(context.scene, "ts4ct_show_ref", icon="TRIA_DOWN" if context.scene.ts4ct_show_ref else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text="REF", icon='MESH_CUBE')
        if context.scene.ts4ct_show_ref:
            col = box.column()
            col.operator("object.reref", text="Rename Mesh: REF")
            col.operator("object.sii_subdivision", text="Subdivide REF Mesh")
            col.operator("object.delete_ref_mesh", text="Delete REF Mesh")

        # Mesh
        box = layout.box()
        row = box.row()
        row.prop(context.scene, "ts4ct_show_mesh", icon="TRIA_DOWN" if context.scene.ts4ct_show_mesh else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text="Mesh", icon='OUTLINER_OB_MESH')
        if context.scene.ts4ct_show_mesh:
            col = box.column()
            col.operator("object.resfs", text="Rename Mesh: S4S")
            col.operator("object.rdmbd", text="Merge by Distance")
            col.operator("object.s4studio_set_cut_number", text="Set Cut Number (NEED S4S)")
            col.operator("object.quadfa", text="Tris To Quads")
            col.operator("object.trifa", text="Triangulate Faces")

        # UVs
        box = layout.box()
        row = box.row()
        row.prop(context.scene, "ts4ct_show_uvs", icon="TRIA_DOWN" if context.scene.ts4ct_show_uvs else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text="UVs", icon='UV')
        if context.scene.ts4ct_show_uvs:
            col = box.column()
            col.operator("object.si_uvchecker", text="UV Checker")
            col.operator("object.siii_datatrans", text="Data Transfer")

        # Weights
        box = layout.box()
        row = box.row()
        row.prop(context.scene, "ts4ct_show_weights", icon="TRIA_DOWN" if context.scene.ts4ct_show_weights else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text="Weights", icon='MOD_VERTEX_WEIGHT')
        if context.scene.ts4ct_show_weights:
            col = box.column()
            col.operator("object.siiii_weights", text="Weight Transfer")
            col.operator("object.smoothwe", text="Smooth Weights")
            col.operator("object.limwe", text="Limit Weights")

        # Auto Height
        box = layout.box()
        row = box.row()
        row.prop(context.scene, "ts4ct_show_auto_height", icon="TRIA_DOWN" if context.scene.ts4ct_show_auto_height else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text="Auto Height", icon='EMPTY_SINGLE_ARROW')
        if context.scene.ts4ct_show_auto_height:
            col = box.column()
            col.operator("object.add_shoe_height_cut", text="Add Shoe Height Cut Plane")
            col.operator("object.rename_ash", text="Rename Mesh: Add _ASH")
            col.operator("object.find_ash_lowest", text="Calculate Z")
            col.operator("object.calculate_selected_z", text="Calculate Z from Selected Face")
            row = col.row()
            row.prop(context.scene, "ash_lowest_z", text="Lowest Z")

        # Transparency Fix
        box = layout.box()
        row = box.row()
        row.prop(context.scene, "ts4ct_show_transparency", icon="TRIA_DOWN" if context.scene.ts4ct_show_transparency else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text="Transparency", icon='MATERIAL')
        if context.scene.ts4ct_show_transparency:
            col = box.column()
            col.operator("mesh.mark_strip", text="Mark Boundary")
            col.operator("mesh.clear_strip", text="Clear Boundary")
            col.operator("mesh.transparency_fix", text="Fix Transparency")

        # LOD Creation
        box = layout.box()
        row = box.row()
        row.prop(context.scene, "ts4ct_show_lods", icon="TRIA_DOWN" if context.scene.ts4ct_show_lods else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text="LODs", icon='SNAP_VERTEX')
        if context.scene.ts4ct_show_lods:
            col = box.column()
            col.operator("mesh.generate_lod_levels", text="Generate LOD Levels")
            col.operator("mesh.mark_lod_vertices", text="Mark LOD Connection Boundary")
            col.operator("mesh.clear_lod_vertices", text="Clear LOD Connection Boundary")
            col.operator("mesh.connect_lod_vertices", text="Connect LOD Vertices")

            # Dynamic wireframe toggle button
            if context.space_data.shading.type == 'WIREFRAME':
                col.operator("mesh.turn_off_wireframe", text="Wireframe Mode Off")
            else:
                col.operator("mesh.setup_wireframe_snap", text="Wireframe Mode On")

        # Vertex Paints
        box = layout.box()
        row = box.row()
        row.prop(context.scene, "ts4ct_show_vertex_paints", icon="TRIA_DOWN" if context.scene.ts4ct_show_vertex_paints else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text="Vertex Paints", icon='VPAINT_HLT')
        if context.scene.ts4ct_show_vertex_paints:
            col = box.column()
            col.operator("object.vtc_skintight", text="Skin Tight")
            col.operator("object.vtc_robemorph", text="Robe Morph")
            col.operator("object.vtc_hairline", text="Hairline")
            col.operator("object.vtc_hairacc", text="Hair Acc")
            col.operator("object.vtc_black", text="Black/NONE")
            col.operator("object.vtc_white", text="White/Lamp Glow")

        # Bake
        box = layout.box()
        row = box.row()
        row.prop(context.scene, "ts4ct_show_bake", icon="TRIA_DOWN" if context.scene.ts4ct_show_bake else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text="Shadow Map", icon='SHADING_RENDERED')
        if context.scene.ts4ct_show_bake:
            col = box.column()
            col.operator("tsct.create_shadow_bake_collection", text="Create Bake Collection")
            col.operator("tsct.open_shadow_bake", text="Shadow Map")

        # Texture Transfer
        box = layout.box()
        row = box.row()
        row.prop(context.scene, "ts4ct_show_texture_transfer", icon="TRIA_DOWN" if context.scene.ts4ct_show_texture_transfer else "TRIA_RIGHT", icon_only=True, emboss=False)
        row.label(text="Baking", icon='TEXTURE')
        if context.scene.ts4ct_show_texture_transfer:
            col = box.column()
            col.operator("tsct.duplicate_to_texturetransfer", text="Create Bake Duplicate")
            col.operator("tsct.setup_materials", text="Setup Materials")
            col.operator("tsct.setup_uv_maps", text="Setup UV Maps")
            
            # Enhanced batch baking workflow - Primary method
            batch_box = col.box()
            batch_box.label(text="Baking", icon='RENDER_STILL')
            batch_col = batch_box.column()
            
            # Start batch bake (moved to top for visibility during progress)
            if context.scene.ts4ct_bake_active:
                # Show progress during baking
                progress_box = batch_col.box()
                progress_box.label(text="Baking in Progress", icon='RENDER_STILL')
                
                # Progress bar
                progress_row = progress_box.row()
                progress_row.prop(context.scene, "ts4ct_bake_progress", slider=True, text="Progress")
                
                # Status text
                progress_box.label(text=context.scene.ts4ct_bake_status, icon='INFO')
                
                # Cancel button
                cancel_row = progress_box.row()
                cancel_row.operator("tsct.cancel_batch_bake", text="Cancel Baking (ESC)", icon='CANCEL')
            else:
                # Normal start batch bake button
                batch_col.operator("tsct.start_batch_texture_bake", text="Start Baking", icon='RENDER_STILL')
            
            # Batch Queue Management
            queue_box = batch_col.box()
            queue_box.label(text="Mesh Queue", icon='MESH_DATA')
            
            # Mesh list and controls in a horizontal layout
            queue_main_row = queue_box.row()
            
            # Mesh list (takes most of the space)
            queue_list_row = queue_main_row.row()
            queue_list_row.template_list("TSCT_UL_TextureQueues", "texture_queues", context.scene, "ts4ct_texture_queues", context.scene, "ts4ct_active_queue_index")
            
            # Mesh control buttons (vertical stack)
            queue_controls = queue_main_row.column(align=True)
            queue_controls.operator("tsct.create_mesh_queue", text="", icon='ADD')
            queue_controls.operator("tsct.remove_mesh_from_queue", text="", icon='REMOVE')

            # Current queue details
            if len(context.scene.ts4ct_texture_queues) > 0:
                active_index = context.scene.ts4ct_active_queue_index
                if active_index < len(context.scene.ts4ct_texture_queues):
                    queue_entry = context.scene.ts4ct_texture_queues[active_index]

                    # Images management box
                    img_box = queue_box.box()
                    img_box.label(text="Image Queue", icon='FILE_IMAGE')
                    
                    # Images list and controls in a horizontal layout
                    img_main_row = img_box.row()
                    
                    # Images list (takes most of the space)
                    img_list_row = img_main_row.row()
                    img_list_row.template_list("TSCT_UL_QueueImages", "queue_images", queue_entry, "images", queue_entry, "active_image_index")
                    
                    # Image control buttons (vertical stack)
                    img_controls = img_main_row.column(align=True)
                    img_controls.operator("tsct.add_image_to_mesh_queue", text="", icon='ADD')
                    img_controls.operator("tsct.remove_image_from_queue", text="", icon='REMOVE')
                    
                    # Output folder at the bottom
                    img_box.prop(queue_entry, "output_folder", text="Output Folder")

# Custom Asset Importer Panel (separate tab)
class TS4CT_PT_custom_importer(bpy.types.Panel):
    bl_label = "Custom Asset Importer"
    bl_idname = "TS4CT_PT_custom_importer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'TS4CT: Custom Importer'

    def draw(self, context):
        layout = self.layout
        
        # Import the function from ci_asset_management to check folder status
        from .ci_asset_management import check_custom_assets_setup
        
        # Dynamic Setup/Open section
        setup_box = layout.box().column()
        folders_exist = check_custom_assets_setup()
        
        if folders_exist:
            setup_box.label(text="Asset Folder", icon='FILE_FOLDER')
            setup_box.operator("tsct.manage_custom_assets", text="Open Assets Folder")
            
            # Asset loaders section - only show if folders exist
            loader_box = layout.box().column()
            loader_box.label(text="CAS", icon='MOD_CLOTH')
            col = loader_box.column(align=True)
            col.operator("tsct.load_custom_cas", text="Load CAS Part")
            
            loader_box = layout.box().column()
            loader_box.label(text="Body", icon='OUTLINER_OB_MESH')
            col = loader_box.column(align=True)
            col.operator("tsct.load_custom_body", text="Load Body")
            
            loader_box = layout.box().column()
            loader_box.label(text="Rig", icon='ARMATURE_DATA')
            col = loader_box.column(align=True)
            col.operator("tsct.load_custom_rig", text="Load Rig")
            col.operator("object.linkrig", text="Link Rig")

            loader_box = layout.box().column()
            loader_box.label(text="Animations", icon='ANIM')
            col = loader_box.column(align=True)
            col.operator("tsct.load_custom_anim", text="Load Anim")
            col.operator("object.restore_anim", text="Clear Anim")
        else:
            setup_box.label(text="Setup", icon='SETTINGS')
            setup_box.operator("tsct.manage_custom_assets", text="Setup Folders")
            
        # Add preferences button
        setup_box = layout.box().column()
        setup_box.label(text="Settings", icon='PREFERENCES')
        setup_box.operator("tsct.open_preferences", text="Folder Path Settings")

# Register And Unregister
def register():
    # Register preference classes
    user_preferences.register()
    
    # Register panels
    bpy.utils.register_class(CUUPID_PT_creator_tools)
    bpy.utils.register_class(TS4CT_PT_custom_importer)

    # Register collapsible panel properties
    bpy.types.Scene.ts4ct_show_asset_importer = bpy.props.BoolProperty(
        name="Show Asset Importer",
        default=True,
        description="Toggle Asset Importer section visibility"
    )
    bpy.types.Scene.ts4ct_show_anim_importer = bpy.props.BoolProperty(
        name="Show Anim Importer",
        default=True,
        description="Toggle Anim Importer section visibility"
    )
    bpy.types.Scene.ts4ct_show_ref = bpy.props.BoolProperty(
        name="Show REF",
        default=True,
        description="Toggle REF section visibility"
    )
    bpy.types.Scene.ts4ct_show_mesh = bpy.props.BoolProperty(
        name="Show Mesh",
        default=True,
        description="Toggle Mesh section visibility"
    )
    bpy.types.Scene.ts4ct_show_uvs = bpy.props.BoolProperty(
        name="Show UVs",
        default=True,
        description="Toggle UVs section visibility"
    )
    bpy.types.Scene.ts4ct_show_weights = bpy.props.BoolProperty(
        name="Show Weights",
        default=True,
        description="Toggle Weights section visibility"
    )
    bpy.types.Scene.ts4ct_show_auto_height = bpy.props.BoolProperty(
        name="Show Auto Height",
        default=True,
        description="Toggle Auto Height section visibility"
    )
    bpy.types.Scene.ts4ct_show_transparency = bpy.props.BoolProperty(
        name="Show Transparency",
        default=True,
        description="Toggle Transparency section visibility"
    )
    bpy.types.Scene.ts4ct_show_lods = bpy.props.BoolProperty(
        name="Show LODs",
        default=True,
        description="Toggle LODs section visibility"
    )
    bpy.types.Scene.ts4ct_show_vertex_paints = bpy.props.BoolProperty(
        name="Show Vertex Paints",
        default=True,
        description="Toggle Vertex Paints section visibility"
    )
    bpy.types.Scene.ts4ct_show_bake = bpy.props.BoolProperty(
        name="Show Shadow Map",
        default=True,
        description="Toggle Shadow Map section visibility"
    )
    bpy.types.Scene.ts4ct_show_texture_transfer = bpy.props.BoolProperty(
        name="Show Bake",
        default=True,
        description="Toggle Bake section visibility"
    )
    
    # Import TextureQueueEntry from user_preferences for scene properties
    from .user_preferences import TSCT_TextureQueueEntry
    
    bpy.types.Scene.ts4ct_texture_queues = bpy.props.CollectionProperty(
        type=TSCT_TextureQueueEntry,
        name="Texture Queues",
        description="Per-mesh image queues for batch texture baking"
    )
    bpy.types.Scene.ts4ct_active_queue_index = bpy.props.IntProperty(
        name="Active Queue",
        default=0
    )
    
    # Progress tracking for batch baking
    bpy.types.Scene.ts4ct_bake_progress = bpy.props.FloatProperty(
        name="Bake Progress",
        default=0.0,
        min=0.0,
        max=100.0,
        description="Progress percentage for batch baking"
    )
    bpy.types.Scene.ts4ct_bake_status = bpy.props.StringProperty(
        name="Bake Status",
        default="",
        description="Status message for batch baking"
    )
    bpy.types.Scene.ts4ct_bake_active = bpy.props.BoolProperty(
        name="Bake Active",
        default=False,
        description="Whether batch baking is currently running"
    )
    
    # Register other modules
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
    pi_cas_loader.register()
    pi_occult_loader.register()
    pi_anim_loader.register()
    pi_lodconnect.register()
    pi_transparency.register()
    pi_bakes.register()
    pi_shoe_height.register()
    pi_errors.register() if hasattr(pi_errors, 'register') else None
    
    # Register custom loader modules
    ci_asset_management.register()
    ci_animation_loader.register()
    ci_body_loader.register()
    ci_cas_loader.register()
    ci_rig_loader.register()

def unregister():
    # Unregister collapsible panel properties
    try:
        del bpy.types.Scene.ts4ct_show_asset_importer
        del bpy.types.Scene.ts4ct_show_anim_importer
        del bpy.types.Scene.ts4ct_show_ref
        del bpy.types.Scene.ts4ct_show_mesh
        del bpy.types.Scene.ts4ct_show_uvs
        del bpy.types.Scene.ts4ct_show_weights
        del bpy.types.Scene.ts4ct_show_auto_height
        del bpy.types.Scene.ts4ct_show_transparency
        del bpy.types.Scene.ts4ct_show_lods
        del bpy.types.Scene.ts4ct_show_vertex_paints
        del bpy.types.Scene.ts4ct_show_bake
        del bpy.types.Scene.ts4ct_show_texture_transfer
        del bpy.types.Scene.ts4ct_texture_queues
        del bpy.types.Scene.ts4ct_active_queue_index
        del bpy.types.Scene.ts4ct_bake_progress
        del bpy.types.Scene.ts4ct_bake_status
        del bpy.types.Scene.ts4ct_bake_active
    except AttributeError:
        pass

    # Unregister panels
    bpy.utils.unregister_class(CUUPID_PT_creator_tools)
    bpy.utils.unregister_class(TS4CT_PT_custom_importer)
    
    # Unregister other modules
    si_uvchecker.unregister()
    pi_mesh.unregister()
    pi_vertex_paint.unregister()
    pi_prereq.unregister()
    pi_base_loader.unregister()
    pi_rig_loader.unregister()
    pi_weights.unregister()
    pi_cutnum.unregister()
    pi_rig_link.unregister()
    pi_datatransfer.unregister()
    pi_bone_shape_destroyer.unregister()
    pi_wiresnap.unregister()
    lodeci.unregister()
    pi_cas_loader.unregister()
    pi_occult_loader.unregister()
    pi_anim_loader.unregister()
    pi_lodconnect.unregister()
    pi_transparency.unregister()
    pi_bakes.unregister()
    pi_shoe_height.unregister()
    pi_errors.unregister() if hasattr(pi_errors, 'unregister') else None
    
    # Unregister custom loader modules
    ci_asset_management.unregister()
    ci_animation_loader.unregister()
    ci_body_loader.unregister()
    ci_cas_loader.unregister()
    ci_rig_loader.unregister()
    
    # Unregister preference classes
    user_preferences.unregister()

# Only register when running as addon
if __name__ == "__main__":
    register()