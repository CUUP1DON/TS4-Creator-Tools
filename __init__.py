import bpy
import os
from bpy.types import AddonPreferences
from bpy.props import StringProperty, CollectionProperty, BoolProperty, IntProperty

# Add custom Imports Here
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
from . import pi_anim_loader
from . import pi_lodconnect
from . import pi_transparency
from . import pi_bakes

#Custom Loader
from . import ci_asset_management
from . import ci_animation_loader
from . import ci_body_loader
from . import ci_cas_loader
from . import ci_rig_loader


# Blender Addon Info
bl_info = {
    "name": "TS4 Creator Tools",
    "author": "CUUPIDON",
    "version": (1, 8),
    "blender": (3, 6, 9),
    "location": "View3D > Sidebar > TS4CT",
    "description": "Tools to take tedium out of the work flow.",
    "category": "Object",
}

# Path entry for the list of asset directories
class TSCT_AssetPathEntry(bpy.types.PropertyGroup):
    path: StringProperty(
        name="Directory Path",
        description="Path to a directory for storing custom assets",
        default="",
        subtype='DIR_PATH'
    )
    enabled: BoolProperty(
        name="Enabled",
        description="Whether this path is active",
        default=True
    )

# Addon preferences
class TSCT_Preferences(AddonPreferences):
    bl_idname = __name__

    asset_paths: CollectionProperty(
        type=TSCT_AssetPathEntry,
        name="Asset Directories",
        description="List of directories for storing custom assets"
    )
    
    active_path_index: IntProperty(
        name="Active Asset Path",
        default=0
    )
    
    use_default_directory: BoolProperty(
        name="Use Default Directory",
        description="Use the default directory in Documents/Sims 4 Creator Tools",
        default=True,
        update=lambda self, context: self._update_directory_selection(context, 'default')
    )
    
    use_custom_directories: BoolProperty(
        name="Use Custom Asset Directories",
        description="Use custom asset directories instead of the default",
        default=False,
        update=lambda self, context: self._update_directory_selection(context, 'custom')
    )
    
    def _update_directory_selection(self, context, option):
        """Handle mutual exclusivity between directory options"""
        if option == 'default' and self.use_default_directory:
            self.use_custom_directories = False
        elif option == 'custom' and self.use_custom_directories:
            self.use_default_directory = False

    def draw(self, context):
        layout = self.layout
        
        # Main directory options with mutual exclusivity
        box = layout.box()
        box.label(text="Asset Directory Configuration", icon='FILE_FOLDER')
        
        # Default directory option
        row = box.row()
        row.prop(self, "use_default_directory")
        
        if self.use_default_directory:
            default_path = os.path.join(os.path.expanduser("~"), "Documents", "Sims 4 Creator Tools")
            info_box = box.box()
            info_box.label(text=f"Default path: {default_path}", icon='INFO')
        
        # Custom directories option
        row = box.row()
        row.prop(self, "use_custom_directories")
        
        # Custom asset directories section - only show when enabled
        if self.use_custom_directories:
            custom_box = layout.box()
            custom_box.label(text="Custom Asset Directories", icon='FOLDER_REDIRECT')
            
            # Header row for the list
            header_row = custom_box.row()
            header_split = header_row.split(factor=0.7)
            header_split.label(text="Path")
            header_split.label(text="Enabled")
            
            # List and buttons
            list_row = custom_box.row()
            list_row.template_list("TSCT_UL_AssetPaths", "", self, "asset_paths", self, "active_path_index")
            
            # Add/Remove buttons
            col = list_row.column(align=True)
            col.operator("tsct.add_asset_path", icon='ADD', text="")
            col.operator("tsct.remove_asset_path", icon='REMOVE', text="")

            # Show selected path details
            if len(self.asset_paths) > 0 and self.active_path_index < len(self.asset_paths):
                path_entry = self.asset_paths[self.active_path_index]
                details_row = custom_box.row()
                details_row.prop(path_entry, "path", text="")

# UI List for asset paths
class TSCT_UL_AssetPaths(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.8)
            split.label(text=item.path if item.path else "Click to set path")
            split.prop(item, "enabled", text="")
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.prop(item, "enabled", text="")

# Operator to add an asset path
class TSCT_OT_AddAssetPath(bpy.types.Operator):
    """Add a new asset directory path"""
    bl_idname = "tsct.add_asset_path"
    bl_label = "Add Asset Directory"
    bl_options = {'REGISTER', 'INTERNAL'}
    
    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        new_path = prefs.asset_paths.add()
        prefs.active_path_index = len(prefs.asset_paths) - 1
        return {'FINISHED'}

# Operator to remove an asset path
class TSCT_OT_RemoveAssetPath(bpy.types.Operator):
    """Remove the selected asset directory path"""
    bl_idname = "tsct.remove_asset_path" 
    bl_label = "Remove Asset Directory"
    bl_options = {'REGISTER', 'INTERNAL'}
    
    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        if prefs.asset_paths and prefs.active_path_index < len(prefs.asset_paths):
            prefs.asset_paths.remove(prefs.active_path_index)
            prefs.active_path_index = min(prefs.active_path_index, len(prefs.asset_paths) - 1)
        return {'FINISHED'}

# Operator to open addon preferences
class TSCT_OT_OpenPreferences(bpy.types.Operator):
    """Open addon preferences to configure asset paths"""
    bl_idname = "tsct.open_preferences"
    bl_label = "Open Asset Paths Settings"
    
    def execute(self, context):
        bpy.ops.preferences.addon_show(module=__name__)
        return {'FINISHED'}

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
        assetimport_menu = layout.box().column()
        assetimport_menu.label(text="Asset Importer", icon='MESH_MONKEY')
        assetimport_menu.operator("object.load_body_base", text="Load Body Base...")
        assetimport_menu.operator("object.load_cas", text="Load CAS Items...")

        # Anim Importer
        animimport_menu = layout.box().column()
        animimport_menu.label(text="Anim Importer", icon='ARMATURE_DATA')
        animimport_menu.operator("object.load_rig", text="Load Rig...")
        animimport_menu.operator("object.linkrig", text="Link Rig")
        animimport_menu.operator("object.load_anim", text="Load Animation...")
        animimport_menu.operator("object.restore_anim", text="Clear Animation")
        
        # REF
        ref_menu = layout.box().column()
        ref_menu.label(text="REF", icon='MESH_CUBE')
        ref_menu.operator("object.reref", text="Rename Mesh: REF")
        ref_menu.operator("object.sii_subdivision", text="Subdivide REF Mesh")
        ref_menu.operator("object.delete_ref_mesh", text="Delete REF Mesh")

        # Mesh
        mesh_menu = layout.box().column()
        mesh_menu.label(text="Mesh", icon='OUTLINER_OB_MESH')
        mesh_menu.operator("object.resfs", text="Rename Mesh: S4S")
        mesh_menu.operator("object.rdmbd", text="Merge by Distance")
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
        weights_menu.operator("object.siiii_weights", text="Weight Transfer")
        weights_menu.operator("object.smoothwe", text="Smooth Weights")
        weights_menu.operator("object.limwe", text="Limit Weights")
        
        # Transparency Fix
        transparency_menu = layout.box().column()
        transparency_menu.label(text="Transparency", icon='MATERIAL')
        transparency_menu.operator("mesh.mark_strip", text="Mark Boundary")
        transparency_menu.operator("mesh.clear_strip", text="Clear Boundary")
        transparency_menu.operator("mesh.transparency_fix", text="Fix Transparency")

        # LOD Creation
        lod_menu = layout.box().column()
        lod_menu.label(text="LODs", icon='SNAP_VERTEX')
        lod_menu.operator("mesh.generate_lod_levels", text="Generate LOD Levels")
        lod_menu.operator("mesh.mark_lod_vertices", text="Mark LOD Connection Boundary")
        lod_menu.operator("mesh.clear_lod_vertices", text="Clear LOD Connection Boundary")
        lod_menu.operator("mesh.connect_lod_vertices", text="Connect LOD Vertices")
        
        # Dynamic wireframe toggle button
        if context.space_data.shading.type == 'WIREFRAME':
            lod_menu.operator("mesh.turn_off_wireframe", text="Wireframe Mode Off")
        else:
            lod_menu.operator("mesh.setup_wireframe_snap", text="Wireframe Mode On")
        
        # Vertex Paints
        vertex_paints_menu = layout.box().column()
        vertex_paints_menu.label(text="Vertex Paints", icon='VPAINT_HLT')
        vertex_paints_menu.operator("object.vtc_skintight", text="Skin Tight")
        vertex_paints_menu.operator("object.vtc_robemorph", text="Robe Morph")
        vertex_paints_menu.operator("object.vtc_hairline", text="Hairline")
        vertex_paints_menu.operator("object.vtc_hairacc", text="Hair Acc")
        vertex_paints_menu.operator("object.vtc_black", text="Black/NONE")
        vertex_paints_menu.operator("object.vtc_white", text="White/Lamp Glow")

        # Bake
        bakes_menu = layout.box().column()
        bakes_menu.label(text="Bake", icon='SHADING_RENDERED')
        bakes_menu.operator("tsct.create_shadow_bake_collection", text="Create Bake Collection")
        bakes_menu.operator("tsct.open_shadow_bake", text="Shadow Map")

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
    bpy.utils.register_class(TSCT_AssetPathEntry)
    bpy.utils.register_class(TSCT_UL_AssetPaths)
    bpy.utils.register_class(TSCT_Preferences)
    bpy.utils.register_class(TSCT_OT_AddAssetPath)
    bpy.utils.register_class(TSCT_OT_RemoveAssetPath)
    bpy.utils.register_class(TSCT_OT_OpenPreferences)
    bpy.utils.register_class(CUUPID_PT_creator_tools)
    bpy.utils.register_class(TS4CT_PT_custom_importer)
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
    pi_anim_loader.register()
    pi_lodconnect.register()
    pi_transparency.register()
    pi_bakes.register()
    pi_errors.register() if hasattr(pi_errors, 'register') else None
    
#customloader
    ci_asset_management.register()
    ci_animation_loader.register()
    ci_body_loader.register()
    ci_cas_loader.register()
    ci_rig_loader.register()


def unregister():
    bpy.utils.unregister_class(TSCT_AssetPathEntry)
    bpy.utils.unregister_class(TSCT_UL_AssetPaths)
    bpy.utils.unregister_class(TSCT_Preferences)
    bpy.utils.unregister_class(TSCT_OT_AddAssetPath)
    bpy.utils.unregister_class(TSCT_OT_RemoveAssetPath)
    bpy.utils.unregister_class(TSCT_OT_OpenPreferences)
    bpy.utils.unregister_class(CUUPID_PT_creator_tools)
    bpy.utils.unregister_class(TS4CT_PT_custom_importer)
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
    pi_anim_loader.unregister()
    pi_lodconnect.unregister()
    pi_transparency.unregister()
    pi_bakes.unregister()
    pi_errors.unregister() if hasattr(pi_errors, 'unregister') else None
    
#customloader
    ci_asset_management.unregister()
    ci_animation_loader.unregister()
    ci_body_loader.unregister()
    ci_cas_loader.unregister()
    ci_rig_loader.unregister()


# Only register when running as addon
if __name__ == "__main__":
    register()

# Legacy Popup Functions (kept for compatibility during migration)
def select_obj(self, context):
    pi_errors.show_no_object_selected()

def exit_edit(self, context):
    pi_errors.show_exit_edit_mode()

def sfs_not_found(self, context):
    pi_errors.ErrorManager.show_error('file_not_found',
                                     custom_message="s4studio_mesh_1 not found.",
                                     custom_details=["Make sure S4Studio mesh is in your scene",
                                                   "Check object naming and visibility"])

def ref_not_found(self, context):
    pi_errors.ErrorManager.show_error('file_not_found',
                                     custom_message="REF object not found.",
                                     custom_details=["Load a REF object first",
                                                   "Make sure REF object is visible"])

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

def display_popup_list(popups):
    """Legacy support function - maintained for compatibility"""
    return pi_errors.display_popup_list(popups)