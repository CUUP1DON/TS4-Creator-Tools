import bpy
from bpy.types import AddonPreferences
from bpy.props import StringProperty, CollectionProperty, BoolProperty, IntProperty, FloatProperty, EnumProperty

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

# Simple string property for image paths
class TSCT_ImagePathEntry(bpy.types.PropertyGroup):
    path: StringProperty(
        name="Image Path",
        description="Path to image file",
        default="",
        subtype='FILE_PATH'
    )

# Texture queue entry for per-mesh image queues
class TSCT_TextureQueueEntry(bpy.types.PropertyGroup):
    mesh_name: StringProperty(
        name="Mesh Name",
        description="Name of the mesh object",
        default=""
    )
    output_folder: StringProperty(
        name="Output Folder",
        description="Folder to save baked images for this mesh",
        default="",
        subtype='DIR_PATH'
    )
    images: CollectionProperty(
        type=TSCT_ImagePathEntry,
        name="Images",
        description="List of image paths for this mesh"
    )
    active_image_index: IntProperty(
        name="Active Image",
        default=0
    )

# Addon preferences
class TSCT_Preferences(AddonPreferences):
    bl_idname = "cuupid"  # Main addon module name

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
    
    # Bake Settings Preferences
    bake_device: EnumProperty(
        name="Render Device",
        description="Device to use for texture baking",
        items=[
            ('AUTO', "Auto Detect", "Automatically detect GPU if available, otherwise use CPU"),
            ('GPU', "GPU", "Use GPU for baking (requires CUDA/HIP/OptiX)"),
            ('CPU', "CPU", "Use CPU for baking")
        ],
        default='AUTO'
    )
    
    bake_samples: IntProperty(
        name="Samples",
        description="Number of samples for texture baking",
        default=50,
        min=1,
        max=1000
    )
    
    bake_margin: IntProperty(
        name="Margin",
        description="Margin around baked UV islands in pixels",
        default=10,
        min=0,
        max=100
    )
    
    bake_image_width: IntProperty(
        name="Image Width",
        description="Width of the new bake image in pixels",
        default=2048,
        min=256,
        max=8192
    )
    
    bake_image_height: IntProperty(
        name="Image Height",
        description="Height of the new bake image in pixels",
        default=4096,
        min=256,
        max=8192
    )
    
    bake_use_color: BoolProperty(
        name="Include Color",
        description="Include color in bake",
        default=True
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
            import os
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
        
        # Bake Settings Configuration
        bake_box = layout.box()
        bake_box.label(text="Batch Bake Settings", icon='SHADING_RENDERED')
        
        # Device selection
        bake_box.prop(self, "bake_device")
        
        # Bake parameters
        bake_row = bake_box.row()
        bake_row.prop(self, "bake_samples")
        bake_row.prop(self, "bake_margin")
        
        # Bake image dimensions
        dim_row = bake_box.row()
        dim_row.prop(self, "bake_image_width")
        dim_row.prop(self, "bake_image_height")
        
        # Pass options
        pass_box = bake_box.box()
        pass_box.label(text="Bake Pass Options", icon='NODE_COMPOSITING')
        pass_box.prop(self, "bake_use_color", text="Include Color")
        
        # Reset to defaults button
        reset_row = bake_box.row()
        reset_row.operator("tsct.reset_bake_settings", text="Reset to Defaults", icon='FILE_REFRESH')

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

# UI List for texture queues
class TSCT_UL_TextureQueues(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.7)
            split.label(text=item.mesh_name, icon='MESH_DATA')
            split.label(text=f"{len(item.images)} images")
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.mesh_name, icon='MESH_DATA')

# UI List for images in texture queues
class TSCT_UL_QueueImages(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.path if item.path else "No path", icon='FILE_IMAGE')
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="Image", icon='FILE_IMAGE')

# Operator to add an asset path
class TSCT_OT_AddAssetPath(bpy.types.Operator):
    """Add a new asset directory path"""
    bl_idname = "tsct.add_asset_path"
    bl_label = "Add Asset Directory"
    bl_options = {'REGISTER', 'INTERNAL'}
    
    def execute(self, context):
        addon_name = "cuupid"  # Main addon module name
        if addon_name in context.preferences.addons:
            prefs = context.preferences.addons[addon_name].preferences
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
        addon_name = "cuupid"  # Main addon module name
        if addon_name in context.preferences.addons:
            prefs = context.preferences.addons[addon_name].preferences
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
        addon_name = "cuupid"  # Main addon module name
        bpy.ops.preferences.addon_show(module=addon_name)
        return {'FINISHED'}

# Operator to reset bake settings to defaults
class TSCT_OT_ResetBakeSettings(bpy.types.Operator):
    """Reset bake settings to default values"""
    bl_idname = "tsct.reset_bake_settings"
    bl_label = "Reset Bake Settings"
    bl_description = "Reset all bake settings to default values"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        # Get the addon preferences using the correct module name
        addon_name = "cuupid"  # Main addon module name
        if addon_name in context.preferences.addons:
            prefs = context.preferences.addons[addon_name].preferences
            prefs.bake_device = 'AUTO'
            prefs.bake_samples = 50
            prefs.bake_margin = 10
            prefs.bake_image_width = 2048
            prefs.bake_image_height = 4096
            prefs.bake_use_color = True
            
            # Show confirmation message
            from . import pi_errors
            pi_errors.ErrorManager.show_success('settings_reset_complete')
        else:
            # Fallback message if preferences can't be accessed
            from . import pi_errors
            pi_errors.ErrorManager.show_error('preferences_access_error')
        return {'FINISHED'}

# Registration
def register():
    bpy.utils.register_class(TSCT_AssetPathEntry)
    bpy.utils.register_class(TSCT_ImagePathEntry)
    bpy.utils.register_class(TSCT_TextureQueueEntry)
    bpy.utils.register_class(TSCT_UL_AssetPaths)
    bpy.utils.register_class(TSCT_UL_TextureQueues)
    bpy.utils.register_class(TSCT_UL_QueueImages)
    bpy.utils.register_class(TSCT_Preferences)
    bpy.utils.register_class(TSCT_OT_AddAssetPath)
    bpy.utils.register_class(TSCT_OT_RemoveAssetPath)
    bpy.utils.register_class(TSCT_OT_OpenPreferences)
    bpy.utils.register_class(TSCT_OT_ResetBakeSettings)

def unregister():
    bpy.utils.unregister_class(TSCT_AssetPathEntry)
    bpy.utils.unregister_class(TSCT_ImagePathEntry)
    bpy.utils.unregister_class(TSCT_TextureQueueEntry)
    bpy.utils.unregister_class(TSCT_UL_AssetPaths)
    bpy.utils.unregister_class(TSCT_UL_TextureQueues)
    bpy.utils.unregister_class(TSCT_UL_QueueImages)
    bpy.utils.unregister_class(TSCT_Preferences)
    bpy.utils.unregister_class(TSCT_OT_AddAssetPath)
    bpy.utils.unregister_class(TSCT_OT_RemoveAssetPath)
    bpy.utils.unregister_class(TSCT_OT_OpenPreferences)
    bpy.utils.unregister_class(TSCT_OT_ResetBakeSettings)