import bpy
import os
import shutil
import subprocess
import tempfile
import atexit
from bpy.types import Operator
from . import pi_errors

# Global list to track temporary files for cleanup
_temp_files = []

def cleanup_temp_files():
    """Clean up temporary files on exit"""
    global _temp_files
    for temp_file in _temp_files[:]:  # Create a copy to iterate over
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            _temp_files.remove(temp_file)
        except Exception:
            pass

# Register cleanup function to run on exit
atexit.register(cleanup_temp_files)


class TSCT_OT_OpenShadowBake(Operator):
    """Open a copy of the shadow map baking setup file"""
    bl_idname = "tsct.open_shadow_bake"
    bl_label = "Shadow Map"
    bl_description = "Open a copy of the shadow map baking setup file"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            # Get the addon directory path
            addon_dir = os.path.dirname(os.path.realpath(__file__))
            original_file_path = os.path.join(addon_dir, "assets", "bake", "sm_bake.blend")
            
            # Check if the original file exists
            if not os.path.exists(original_file_path):
                pi_errors.ErrorManager.show_error('asset_file_missing',
                    custom_message="Shadow bake file not found!",
                    custom_details=[
                        "Expected location: assets/bake/sm_bake.blend",
                        "Please reinstall the addon or contact support"
                    ])
                return {'CANCELLED'}
            
            # Create a temporary copy of the file
            temp_dir = tempfile.gettempdir()
            temp_file_path = os.path.join(temp_dir, "sm_bake_copy.blend")
            
            # Copy the file to temp location
            shutil.copy2(original_file_path, temp_file_path)
            
            # Track temp file for cleanup
            global _temp_files
            _temp_files.append(temp_file_path)
            
            # Check if Baking collection exists and import it
            baking_collection = bpy.data.collections.get("Baking")
            if baking_collection and len(baking_collection.objects) > 0:
                # Save current blend file to temp location for collection import
                current_file_path = os.path.join(temp_dir, "current_baking_source.blend")
                bpy.ops.wm.save_as_mainfile(filepath=current_file_path, copy=True)
                
                # Track temp file for cleanup
                _temp_files.append(current_file_path)
                
                # Create a Python script to import the Baking collection
                import_script = f'''
import bpy
import os

# Import the Baking collection from the source file
source_file = r"{current_file_path}"
if os.path.exists(source_file):
    # Append the Baking collection
    with bpy.data.libraries.load(source_file) as (data_from, data_to):
        if "Baking" in data_from.collections:
            data_to.collections = ["Baking"]
    
    # Link the imported collection to the scene
    if "Baking" in bpy.data.collections:
        imported_collection = bpy.data.collections["Baking"]
        if imported_collection.name not in bpy.context.scene.collection.children:
            bpy.context.scene.collection.children.link(imported_collection)
        print("Baking collection imported successfully!")
    else:
        print("Failed to import Baking collection")
else:
    print("Source file not found for collection import")
'''
                
                # Save the import script to temp location
                script_file_path = os.path.join(temp_dir, "import_baking_collection.py")
                with open(script_file_path, 'w') as script_file:
                    script_file.write(import_script)
                
                # Track script file for cleanup
                _temp_files.append(script_file_path)
                
                # Get the current Blender executable path
                blender_exe = bpy.app.binary_path
                
                # Launch new Blender instance with the copied file and run the import script
                # Use proper subprocess management with error handling
                try:
                    process = subprocess.Popen([blender_exe, temp_file_path, "--python", script_file_path])
                    # Don't wait for the process to finish as it's a new Blender instance
                except Exception as e:
                    # Clean up temp files if subprocess fails
                    cleanup_temp_files()
                    raise e
                
                # Count meshes for success message
                mesh_count = len([obj for obj in baking_collection.objects if obj.type == 'MESH'])
                
                pi_errors.ErrorManager.show_success('bake_file_opened',
                    custom_message=f"Shadow bake opened with {mesh_count} imported meshes!",
                    custom_details=["Ready for shadow map baking"])
            else:
                # No Baking collection or it's empty - just open the file
                blender_exe = bpy.app.binary_path
                try:
                    process = subprocess.Popen([blender_exe, temp_file_path])
                    # Don't wait for the process to finish as it's a new Blender instance
                except Exception as e:
                    # Clean up temp files if subprocess fails
                    cleanup_temp_files()
                    raise e
                
                pi_errors.ErrorManager.show_success('bake_file_opened',
                    custom_message="Shadow bake file opened in new window.",
                    custom_details=[
                        "To import meshes automatically:",
                        "1. Create a 'Baking' collection",
                        "2. Add your meshes to it",
                        "3. Use this button to import them"
                    ])
            
            return {'FINISHED'}
            
        except Exception as e:
            pi_errors.ErrorManager.show_error('operation_failed',
                custom_message="Failed to open shadow bake file!",
                custom_details=[
                    "This could be due to:",
                    "• Missing sm_bake.blend file",
                    "• File permission issues",
                    "• Blender executable not found"
                ],
                additional_info=[f"Error: {str(e)}"])
            return {'CANCELLED'}


class TSCT_OT_CreateShadowBakeCollection(Operator):
    """Create a collection for shadow bake meshes"""
    bl_idname = "tsct.create_shadow_bake_collection"
    bl_label = "Create Bake Collection"
    bl_description = "Create a collection to organize meshes for shadow baking"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            # Collection name
            collection_name = "Baking"
            
            # Check if collection already exists
            if collection_name in bpy.data.collections:
                existing_collection = bpy.data.collections[collection_name]
                
                # Make sure it's linked to the scene if not already
                if existing_collection.name not in context.scene.collection.children:
                    context.scene.collection.children.link(existing_collection)
                
                pi_errors.ErrorManager.show_popup('collection_created',
                    custom_message="Baking collection already exists!",
                    custom_details=[
                        "You can add meshes to the existing",
                        "Baking collection."
                    ])
                return {'FINISHED'}
            
            # Create new collection
            new_collection = bpy.data.collections.new(collection_name)
            
            # Link it to the scene
            context.scene.collection.children.link(new_collection)
            
            pi_errors.ErrorManager.show_success('collection_created')
            
            return {'FINISHED'}
            
        except Exception as e:
            pi_errors.ErrorManager.show_error('blender_context_error',
                custom_message="Failed to create baking collection!",
                custom_details=[
                    "This could be due to:",
                    "• Scene permission issues",
                    "• Blender context problems"
                ],
                additional_info=[f"Error: {str(e)}"])
            return {'CANCELLED'}


# Registration
def register():
    bpy.utils.register_class(TSCT_OT_OpenShadowBake)
    bpy.utils.register_class(TSCT_OT_CreateShadowBakeCollection)


def unregister():
    # Clean up any remaining temporary files
    cleanup_temp_files()
    
    # Unregister classes with error handling
    try:
        bpy.utils.unregister_class(TSCT_OT_OpenShadowBake)
    except Exception:
        pass
    
    try:
        bpy.utils.unregister_class(TSCT_OT_CreateShadowBakeCollection)
    except Exception:
        pass


if __name__ == "__main__":
    register()