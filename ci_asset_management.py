import bpy
import os
from bpy.types import Operator
import platform
import subprocess
import shutil

def get_addon_preferences():
    """Get addon preferences"""
    return bpy.context.preferences.addons[__package__].preferences

def get_documents_path():
    """Get the user's Documents folder path across different operating systems"""
    return os.path.join(os.path.expanduser("~"), "Documents")

def get_default_assets_path():
    """Get the default custom assets folder path"""
    return os.path.join(get_documents_path(), "Sims 4 Creator Tools")

# Backward compatibility function
def get_custom_assets_path():
    """Legacy function - returns the default assets path for backward compatibility"""
    return get_default_assets_path()

def get_asset_directories():
    """Get all enabled asset directories"""
    prefs = get_addon_preferences()
    directories = []
    
    # Add default directory if enabled
    if prefs.use_default_directory:
        directories.append(get_default_assets_path())
    
    # Add custom directories if enabled
    for path_entry in prefs.asset_paths:
        if path_entry.enabled and path_entry.path:
            directories.append(path_entry.path)
    
    # If no directories are configured, return the default path
    if not directories:
        directories.append(get_default_assets_path())
    
    return directories

def check_custom_assets_setup():
    """Check if all custom assets folders exist in at least one directory"""
    asset_dirs = get_asset_directories()
    if not asset_dirs:
        return False
        
    required_folders = ["CAS", "Anim", "Body", "Rig"]
    all_folders_exist = False
    
    for base_path in asset_dirs:
        if not os.path.exists(base_path):
            continue
            
        folder_exists = True
        for folder in required_folders:
            folder_path = os.path.join(base_path, folder)
            if not os.path.exists(folder_path):
                folder_exists = False
                break
        
        if folder_exists:
            all_folders_exist = True
            break
    
    return all_folders_exist

def ensure_custom_assets_folders():
    """Create the custom assets folder structure if it doesn't exist"""
    asset_dirs = get_asset_directories()
    
    # If no directories are configured, use the default one
    if not asset_dirs:
        asset_dirs = [get_default_assets_path()]
    
    folders = ["CAS", "Anim", "Body", "Rig"]
    created_folders = []
    
    # Only create folders in the first valid directory
    base_path = asset_dirs[0]
    
    for folder in folders:
        folder_path = os.path.join(base_path, folder)
        if not os.path.exists(folder_path):
            try:
                os.makedirs(folder_path, exist_ok=True)
                created_folders.append(folder)
            except OSError as e:
                print(f"Error creating folder {folder_path}: {e}")
    
    return created_folders

def copy_readme_file():
    """Copy the readme file from assets/readmes to the asset folders"""
    try:
        # Get the addon directory and construct source path
        addon_dir = os.path.dirname(os.path.realpath(__file__))
        source_readme = os.path.join(addon_dir, "assets", "readmes", "readme.txt")
        
        # Get destination paths
        asset_dirs = get_asset_directories()
        if not asset_dirs:
            return False
        
        success = False
        # Copy to each enabled directory
        for dest_dir in asset_dirs:
            dest_readme = os.path.join(dest_dir, "README.txt")
            
            # Check if source file exists
            if os.path.exists(source_readme):
                # Create directory if it doesn't exist
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir, exist_ok=True)
                
                # Copy the file (overwrite if exists)
                shutil.copy2(source_readme, dest_readme)
                print(f"README file copied from {source_readme} to {dest_readme}")
                success = True
        
        return success
    except Exception as e:
        print(f"Error copying README file: {e}")
        return False

def scan_custom_assets(asset_type):
    """Scan for custom assets in all specified folders"""
    asset_dirs = get_asset_directories()
    assets = []
    
    for base_dir in asset_dirs:
        asset_folder = os.path.join(base_dir, asset_type)
        
        if not os.path.exists(asset_folder):
            continue
        
        for item in os.listdir(asset_folder):
            if item.endswith('.blend'):
                assets.append({
                    'name': item[:-6], 
                    'filename': item, 
                    'path': os.path.join(asset_folder, item),
                    'source_folder': base_dir
                })
    
    return assets

def get_available_rigs(context):
    """Get all available armature objects in the scene"""
    rigs = []
    for obj in context.scene.objects:
        if obj.type == 'ARMATURE':
            rigs.append(obj)
    return rigs

def show_popup(message, title="Creator Tools", icon='INFO'):
    """Show popup message"""
    def popup(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(popup, title=title, icon=icon)

def get_asset_items(asset_type):
    """Get available items from the custom folder for EnumProperty"""
    assets = scan_custom_assets(asset_type)
    if not assets:
        return [('NONE', f'No custom {asset_type.lower()} found', 
                f'No custom {asset_type.lower()} found in your configured asset directories')]
    
    return [(asset['filename'], asset['name'], f"Load {asset['name']}") for asset in assets]

def get_rig_items(self, context):
    """Get available rigs for EnumProperty"""
    rigs = get_available_rigs(context)
    if not rigs:
        return [('NONE', 'No rigs found', 'No armature objects found in the scene')]
    
    return [(rig.name, rig.name, f"Apply animation to rig '{rig.name}'") for rig in rigs]

def get_or_create_collection(name, parent=None):
    """Get existing collection or create new one"""
    if name in bpy.data.collections:
        collection = bpy.data.collections[name]
    else:
        collection = bpy.data.collections.new(name)
        if parent:
            parent.children.link(collection)
        else:
            bpy.context.scene.collection.children.link(collection)
    return collection

def find_root_collections(collections):
    """Find collections that are not children of any other collection in the list"""
    root_collections = []
    collection_names = {col.name for col in collections}
    
    for collection in collections:
        is_root = True
        # Check if this collection is a child of any other collection in our list
        for other_collection in collections:
            if other_collection != collection and collection.name in [child.name for child in other_collection.children]:
                is_root = False
                break
        
        if is_root:
            root_collections.append(collection)
    
    return root_collections

class TSCT_OT_manage_custom_assets(Operator):
    """Manage custom assets folder - create or open"""
    bl_idname = "tsct.manage_custom_assets"
    bl_label = "Manage Custom Assets"
    bl_description = "Create folders if they don't exist, or open the assets folder if they do"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        asset_dirs = get_asset_directories()
        
        # If no directories are configured, use the default one
        if not asset_dirs:
            prefs = get_addon_preferences()
            prefs.use_default_directory = True
            asset_dirs = [get_default_assets_path()]
        
        folders_exist = check_custom_assets_setup()
        
        if not folders_exist:
            # Create folders
            created_folders = ensure_custom_assets_folders()
            
            # Copy the README file
            readme_copied = copy_readme_file()
            
            message_parts = []
            if created_folders:
                message_parts.append(f"Created folders in {asset_dirs[0]}")
            else:
                message_parts.append(f"Folders already exist in one of your configured directories")
            
            if readme_copied:
                message_parts.append("README file added")
            
            message = ". ".join(message_parts) + "."
            show_popup(message)
            
            # Force UI refresh to update the button
            for area in context.screen.areas:
                if area.type == 'VIEW_3D':
                    area.tag_redraw()
        else:
            # Open first valid folder
            for assets_path in asset_dirs:
                if os.path.exists(assets_path):
                    try:
                        system = platform.system()
                        if system == "Windows":
                            subprocess.Popen(['explorer', assets_path])
                        elif system == "Darwin":
                            subprocess.Popen(['open', assets_path])
                        else:
                            subprocess.Popen(['xdg-open', assets_path])
                        
                        show_popup(f"Opening folder...")
                        break
                    except Exception as e:
                        show_popup(f"Could not open folder: {str(e)}", icon='ERROR')
        
        return {'FINISHED'}

# Registration
classes = [
    TSCT_OT_manage_custom_assets,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)