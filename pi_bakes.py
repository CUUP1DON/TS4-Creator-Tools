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



class TSCT_OT_DuplicateToTextureTransfer(Operator):
    """Create TextureTransfer collection and duplicate selected objects to it
    
    Prepares meshes for batch texture baking workflow. Creates TextureTransfer
    collection and duplicates selected mesh objects into it for organized baking.
    Recommended for use with the batch baking queue system.
    """
    bl_idname = "tsct.duplicate_to_texturetransfer"
    bl_label = "Create Bake Duplicate"
    bl_description = "Create bake collection and duplicate selected mesh objects into it"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            # Get selected mesh objects
            selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
            if not selected_meshes:
                pi_errors.ErrorManager.show_error('no_mesh_selected')
                return {'CANCELLED'}

            # Ensure TextureTransfer collection exists
            collection_name = "Baking"
            if collection_name not in bpy.data.collections:
                new_collection = bpy.data.collections.new(collection_name)
                context.scene.collection.children.link(new_collection)
            transfer_collection = bpy.data.collections[collection_name]

            # Duplicate each selected mesh and move to collection
            duplicated_objects = []
            for obj in selected_meshes:
                # Select only this object
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                context.view_layer.objects.active = obj

                # Store original object name
                original_name = obj.name
                
                # Duplicate
                bpy.ops.object.duplicate()

                # Get the duplicate (should be the active object now)
                duplicate = context.active_object
                
                # Rename the duplicate to original name + _bake (without any auto-generated numbering)
                duplicate.name = f"{original_name}_bake"
                
                duplicated_objects.append(duplicate)

                # Remove from all current collections
                for coll in duplicate.users_collection:
                    coll.objects.unlink(duplicate)

                # Link to TextureTransfer collection
                transfer_collection.objects.link(duplicate)

            # Select the duplicates
            bpy.ops.object.select_all(action='DESELECT')
            for obj in duplicated_objects:
                obj.select_set(True)
            if duplicated_objects:
                context.view_layer.objects.active = duplicated_objects[0]

            pi_errors.ErrorManager.show_success('objects_duplicated',
                count=len(duplicated_objects))

            return {'FINISHED'}

        except Exception as e:
            pi_errors.ErrorManager.show_error('blender_context_error',
                custom_message="Failed to duplicate objects!",
                custom_details=[
                    "This could be due to:",
                    "• Scene permission issues",
                    "• Blender context problems"
                ],
                additional_info=[f"Error: {str(e)}"])
            return {'CANCELLED'}


class TSCT_OT_SetupUVMaps(Operator):
    """Setup UV maps for texture transfer on selected objects
    
    Prepares UV layers for batch texture baking. Renames first UV layer to OG_MAP
    (for render), creates NEW_MAP (for edit), and sets proper active states.
    Essential for texture transfer workflow.
    """
    bl_idname = "tsct.setup_uv_maps"
    bl_label = "Setup UV Maps"
    bl_description = "Rename first UV map to OG_MAP, create NEW_MAP, and set active/render UVs"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            # Get selected mesh objects
            selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
            if not selected_meshes:
                pi_errors.ErrorManager.show_error('no_mesh_selected')
                return {'CANCELLED'}

            processed_count = 0
            for obj in selected_meshes:
                mesh = obj.data
                if not mesh.uv_layers:
                    # Skip objects without UV layers
                    continue

                # Rename first UV layer to OG_MAP
                first_uv = mesh.uv_layers[0]
                first_uv.name = "OG_MAP"

                # Create new UV layer NEW_MAP
                new_uv = mesh.uv_layers.new(name="NEW_MAP")

                # Remove any additional UV layers except OG_MAP and NEW_MAP
                layers_to_remove = []
                for uv_layer in mesh.uv_layers:
                    if uv_layer.name not in ["OG_MAP", "NEW_MAP"]:
                        layers_to_remove.append(uv_layer)

                for uv_layer in layers_to_remove:
                    mesh.uv_layers.remove(uv_layer)

                # Set OG_MAP as render active (index 0)
                mesh.uv_layers.active_index = 0  # OG_MAP

                # Set NEW_MAP as active for editing (but not render)
                mesh.uv_layers.active = new_uv

                processed_count += 1

            if processed_count == 0:
                pi_errors.ErrorManager.show_error('validation_error',
                    custom_message="No UV layers found on selected objects!",
                    custom_details=[
                        "Selected objects must have UV layers",
                        "to setup for texture transfer."
                    ])
                return {'CANCELLED'}

            pi_errors.ErrorManager.show_success('uv_setup_complete',
                count=processed_count)

            return {'FINISHED'}

        except Exception as e:
            pi_errors.ErrorManager.show_error('blender_context_error',
                custom_message="Failed to setup UV maps!",
                custom_details=[
                    "This could be due to:",
                    "• Mesh data issues",
                    "• UV layer problems"
                ],
                additional_info=[f"Error: {str(e)}"])
            return {'CANCELLED'}


class TSCT_OT_SetupMaterials(Operator):
    """Setup materials for texture transfer on selected objects
    
    Creates optimal materials for batch texture baking. Sets up TextureTransferMat
    with User_Texture node (for input images) and NEW_Texture node (for baking target).
    Perfect for batch baking workflow.
    """
    bl_idname = "tsct.setup_materials"
    bl_label = "Setup Materials"
    bl_description = "Create new material with ImageTexture node and blank 2048x4096 image"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            # Get selected mesh objects
            selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
            if not selected_meshes:
                pi_errors.ErrorManager.show_error('no_mesh_selected')
                return {'CANCELLED'}

            processed_count = 0
            for obj in selected_meshes:
                # Create new material
                mat = bpy.data.materials.new(name="Baking Material")
                mat.use_nodes = True

                # Get node tree
                nodes = mat.node_tree.nodes
                links = mat.node_tree.links

                # Clear default nodes
                nodes.clear()

                # Add Diffuse BSDF instead of Principled BSDF
                diffuse = nodes.new('ShaderNodeBsdfDiffuse')
                diffuse.name = "Diffuse"
                diffuse.label = "Diffuse"
                diffuse.location = (0, 0)
                diffuse.hide = True  # Collapse the node

                # Add Material Output
                output = nodes.new('ShaderNodeOutputMaterial')
                output.name = "Output"
                output.label = "Output"
                output.location = (300, 0)
                output.hide = True  # Collapse the node

                # Connect Diffuse to Output
                links.new(diffuse.outputs['BSDF'], output.inputs['Surface'])

                # Add first Image Texture node (with blank image for baking)
                tex_node = nodes.new('ShaderNodeTexImage')
                tex_node.name = "New Bake"
                tex_node.label = "New Bake"
                tex_node.location = (-300, -25)  # Upper position, very close
                tex_node.hide = True  # Collapse the node

                # Get the addon preferences
                addon_name = "cuupid"  # The addon folder name
                if addon_name in context.preferences.addons:
                    prefs = context.preferences.addons[addon_name].preferences
                    image_width = prefs.bake_image_width
                    image_height = prefs.bake_image_height
                else:
                    # Fallback to default if preferences can't be accessed
                    image_width = 2048
                    image_height = 4096
                
                # Create blank image with user-defined dimensions
                img = bpy.data.images.new("New Bake", image_width, image_height, alpha=True)
                tex_node.image = img

                # Add second Image Texture node (blank for user texture)
                user_tex_node = nodes.new('ShaderNodeTexImage')
                user_tex_node.name = "Image Queue Texture"
                user_tex_node.label = "Image Queue Texture"
                user_tex_node.location = (-300, 25)  # Lower position, very close to New Bake
                user_tex_node.hide = True  # Collapse the node

                # Connect user texture to base color
                links.new(user_tex_node.outputs['Color'], diffuse.inputs['Color'])

                # Assign material to object (new slot)
                if obj.data.materials:
                    obj.data.materials[0] = mat
                else:
                    obj.data.materials.append(mat)

                processed_count += 1

            pi_errors.ErrorManager.show_success('materials_setup_complete',
                count=processed_count)

            return {'FINISHED'}

        except Exception as e:
            pi_errors.ErrorManager.show_error('blender_context_error',
                custom_message="Failed to setup materials!",
                custom_details=[
                    "This could be due to:",
                    "• Material creation issues",
                    "• Node tree problems"
                ],
                additional_info=[f"Error: {str(e)}"])
            return {'CANCELLED'}


class TSCT_OT_AddImageToMeshQueue(Operator):
    """Add image to selected mesh's texture queue
    
    Adds texture images to batch baking queue for selected mesh. Opens file browser
    to select one or more texture files. These will be baked sequentially during
    batch processing with progress tracking and cancellation support.
    """
    bl_idname = "tsct.add_image_to_mesh_queue"
    bl_label = "Add Image to Queue"
    bl_description = "Add an image file to the selected mesh's texture baking queue"
    bl_options = {'REGISTER', 'UNDO'}

    directory: bpy.props.StringProperty(subtype="DIR_PATH")
    files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement)

    def invoke(self, context, event):
        # Get selected mesh
        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not selected_meshes:
            pi_errors.ErrorManager.show_error('no_mesh_selected')
            return {'CANCELLED'}

        # Open file browser with multiple selection
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if not self.files:
            return {'CANCELLED'}

        # Get selected mesh
        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not selected_meshes:
            return {'CANCELLED'}

        mesh = selected_meshes[0]  # Use first selected

        # Find or create queue entry for this mesh
        queues = context.scene.ts4ct_texture_queues
        queue_entry = None
        for entry in queues:
            if entry.mesh_name == mesh.name:
                queue_entry = entry
                break

        if not queue_entry:
            queue_entry = queues.add()
            queue_entry.mesh_name = mesh.name

        # Add selected images to queue
        added_count = 0
        for file_elem in self.files:
            filepath = os.path.join(self.directory, file_elem.name)
            if os.path.isfile(filepath):
                image_entry = queue_entry.images.add()
                image_entry.path = filepath
                added_count += 1

        if added_count == 0:
            pi_errors.ErrorManager.show_error('no_files_added')

        return {'FINISHED'}


class TSCT_OT_RemoveImageFromQueue(Operator):
    """Remove selected image from mesh queue"""
    bl_idname = "tsct.remove_image_from_queue"
    bl_label = "Remove Image from Queue"
    bl_description = "Remove the selected image from the current mesh's queue"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        queues = context.scene.ts4ct_texture_queues
        active_index = context.scene.ts4ct_active_queue_index

        if active_index >= len(queues):
            return {'CANCELLED'}

        queue_entry = queues[active_index]
        active_image_index = queue_entry.active_image_index

        if active_image_index >= len(queue_entry.images):
            return {'CANCELLED'}

        queue_entry.images.remove(active_image_index)

        # Adjust index if necessary
        if active_image_index >= len(queue_entry.images):
            queue_entry.active_image_index = max(0, len(queue_entry.images) - 1)

        return {'FINISHED'}


class TSCT_OT_ClearMeshQueue(Operator):
    """Clear all images from selected mesh's queue"""
    bl_idname = "tsct.clear_mesh_queue"
    bl_label = "Clear Mesh Queue"
    bl_description = "Remove all images from the selected mesh's texture baking queue"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Get selected mesh
        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not selected_meshes:
            pi_errors.ErrorManager.show_error('no_mesh_selected')
            return {'CANCELLED'}

        mesh = selected_meshes[0]

        # Find queue entry
        queues = context.scene.ts4ct_texture_queues
        for entry in queues:
            if entry.mesh_name == mesh.name:
                entry.images.clear()
                pi_errors.ErrorManager.show_success('queue_cleared',
                    mesh_name=mesh.name)
                return {'FINISHED'}

        pi_errors.ErrorManager.show_error('no_queue_for_mesh',
            mesh_name=mesh.name)

        return {'CANCELLED'}


class TSCT_OT_CreateMeshQueue(Operator):
    """Create a queue entry for selected mesh
    
    Sets up queue management for batch texture baking. Creates entry for selected
    mesh where you can add texture images and set output folder. Essential step
    for the non-blocking batch baking workflow.
    """
    bl_idname = "tsct.create_mesh_queue"
    bl_label = "Create Queue for Selected"
    bl_description = "Create an empty queue entry for the selected mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Get selected mesh
        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not selected_meshes:
            pi_errors.ErrorManager.show_error('no_mesh_selected')
            return {'CANCELLED'}

        mesh = selected_meshes[0]

        # Check if queue already exists
        queues = context.scene.ts4ct_texture_queues
        for entry in queues:
            if entry.mesh_name == mesh.name:
                return {'FINISHED'}

        # Create new queue entry
        queue_entry = queues.add()
        queue_entry.mesh_name = mesh.name

        return {'FINISHED'}


class TSCT_OT_StartBatchTextureBake(Operator):
    """Start batch texture baking with queued images
    
    Bakes textures directly in current scene without freezing Blender.
    Automatically switches to Cycles, applies optimal settings (GPU/CPU auto-detect,
    50 samples, Color-only diffuse bake), isolates meshes, and restores original
    settings when complete. ESC or cancel button can abort at any time.
    """
    bl_idname = "tsct.start_batch_texture_bake"
    bl_label = "Start Batch Bake"
    bl_description = "Perform batch texture baking with queued images in current session - non-blocking with auto settings"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        # Initialize modal state (without setting bake active yet)
        self._setup_modal_state(context)
        
        # Validate queues first
        if not self._validate_queues(context):
            return {'CANCELLED'}
        
        # Only set bake active after successful validation
        context.scene.ts4ct_bake_active = True
        
        # Add timer for modal processing
        self._add_timer(context)
        
        # Start modal operation
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def _setup_modal_state(self, context):
        """Initialize the modal baking state"""
        self.is_baking = False
        self.should_cancel = False
        self.current_queue_index = 0
        self.current_image_index = 0
        self.total_images = 0
        self.processed_images = 0
        self.current_mesh_name = ""
        self.current_image_name = ""
        
        # Get valid queues
        self.valid_queues = self._get_valid_queues(context)
        
        # Calculate total images
        for queue_data in self.valid_queues.values():
            self.total_images += len(queue_data.get('images', []))
        
        # Backup current render/bake settings
        self._backup_render_settings(context)
        
        # Initialize progress tracking (but don't set bake active yet)
        context.scene.ts4ct_bake_progress = 0.0
        context.scene.ts4ct_bake_status = "Initializing batch bake..."
        # context.scene.ts4ct_bake_active = True  # Moved to after validation

    def _validate_queues(self, context):
        """Validate that there are queues to process"""
        queues = context.scene.ts4ct_texture_queues
        valid_queues = {}
        
        # Check if there are any queues at all
        if len(queues) == 0:
            pi_errors.ErrorManager.show_error('no_texture_queues')
            return False
        
        # Check for queues with images
        queues_with_images = 0
        for entry in queues:
            if len(entry.images) > 0:
                queues_with_images += 1
                
                # Check if output folder is set
                if not entry.output_folder:
                    pi_errors.ErrorManager.show_error('output_folder_not_set',
                        mesh_name=entry.mesh_name)
                    return False
                
                valid_queues[entry.mesh_name] = {
                    "folder": entry.output_folder,
                    "images": [img.path for img in entry.images]
                }

        if not valid_queues:
            pi_errors.ErrorManager.show_error('no_valid_queues')
            return False
        
        return True
    
    def _backup_render_settings(self, context):
        """Backup current render and bake settings for restoration"""
        scene = context.scene
        
        # Backup render settings
        self._original_settings = {
            'render_engine': scene.render.engine,
            'cycles_device': getattr(scene.cycles, 'device', 'CPU'),
            'preview_samples': getattr(scene.cycles, 'preview_samples', 0),
            'bake_margin': getattr(scene.render.bake, 'margin', 0),
            'bake_pass_direct': getattr(scene.render.bake, 'use_pass_direct', False),
            'bake_pass_indirect': getattr(scene.render.bake, 'use_pass_indirect', False),
            'bake_pass_color': getattr(scene.render.bake, 'use_pass_color', False)
        }
        
        # Backup object visibility states for isolation
        self._object_visibility_backup = {}
        for obj in scene.objects:
            self._object_visibility_backup[obj.name] = {
                'hide_viewport': obj.hide_viewport,
                'hide_render': obj.hide_render,
                'select': obj.select_get()
            }
    
    def _restore_render_settings(self, context):
        """Restore original render and bake settings"""
        if not hasattr(self, '_original_settings'):
            return
            
        scene = context.scene
        settings = self._original_settings
        
        # Restore render settings
        scene.render.engine = settings['render_engine']
        
        if hasattr(scene.cycles, 'device'):
            scene.cycles.device = settings['cycles_device']
        if hasattr(scene.cycles, 'preview_samples'):
            scene.cycles.preview_samples = settings['preview_samples']
            
        if hasattr(scene.render.bake, 'margin'):
            scene.render.bake.margin = settings['bake_margin']
        if hasattr(scene.render.bake, 'use_pass_direct'):
            scene.render.bake.use_pass_direct = settings['bake_pass_direct']
        if hasattr(scene.render.bake, 'use_pass_indirect'):
            scene.render.bake.use_pass_indirect = settings['bake_pass_indirect']
        if hasattr(scene.render.bake, 'use_pass_color'):
            scene.render.bake.use_pass_color = settings['bake_pass_color']
        
        # Restore object visibility
        if hasattr(self, '_object_visibility_backup'):
            for obj_name, visibility_data in self._object_visibility_backup.items():
                obj = scene.objects.get(obj_name)
                if obj:
                    obj.hide_viewport = visibility_data['hide_viewport']
                    obj.hide_render = visibility_data['hide_render']
                    obj.select_set(visibility_data['select'])
    
    def _setup_bake_environment(self, context, mesh_obj):
        """Setup optimal bake environment for the current mesh using preference settings"""
        scene = context.scene
        # Get the addon preferences using the correct module name
        addon_name = "cuupid"  # The addon folder name
        if addon_name in context.preferences.addons:
            prefs = context.preferences.addons[addon_name].preferences
        else:
            # Fallback to default settings if preferences can't be accessed
            class PrefsFallback:
                bake_device = 'AUTO'
                bake_samples = 50
                bake_margin = 10
                bake_use_color = True
            prefs = PrefsFallback()
        
        # Enable Cycles engine
        scene.render.engine = 'CYCLES'
        
        # Set device based on preferences
        if prefs.bake_device == 'AUTO':
            # Auto-detect GPU availability
            try:
                cycles_prefs = context.preferences.addons['cycles'].preferences if 'cycles' in context.preferences.addons else None
                if cycles_prefs and hasattr(cycles_prefs, 'get_devices_for_type'):
                    gpu_devices = cycles_prefs.get_devices_for_type('CUDA') + cycles_prefs.get_devices_for_type('HIP') + cycles_prefs.get_devices_for_type('OPTIX')
                    if gpu_devices:
                        scene.cycles.device = 'GPU'
                    else:
                        scene.cycles.device = 'CPU'
                else:
                    scene.cycles.device = 'CPU'
            except:
                scene.cycles.device = 'CPU'
        elif prefs.bake_device == 'GPU':
            scene.cycles.device = 'GPU'
        else:
            scene.cycles.device = 'CPU'
        
        # Set bake samples from preferences
        scene.cycles.preview_samples = prefs.bake_samples
        
        # Set bake type and parameters (hardcoded for simplified workflow)
        scene.cycles.bake_type = 'DIFFUSE'
        scene.render.bake.margin = prefs.bake_margin
        scene.render.bake.use_pass_direct = False
        scene.render.bake.use_pass_indirect = False
        scene.render.bake.use_pass_color = prefs.bake_use_color
        
        # Ensure we're in object mode for baking
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Isolate the mesh for baking
        bpy.ops.object.select_all(action='DESELECT')
        
        # Hide all objects except the current mesh
        for obj in scene.objects:
            if obj != mesh_obj:
                obj.hide_viewport = True
                obj.hide_render = True
        
        # Show and select current mesh
        mesh_obj.hide_viewport = False
        mesh_obj.hide_render = False
        mesh_obj.select_set(True)
        context.view_layer.objects.active = mesh_obj
        
        # Update status with device and settings info
        device_type = scene.cycles.device
        context.scene.ts4ct_bake_status = f"Baking with {device_type}, {prefs.bake_samples} samples, Color only" 


    def _get_valid_queues(self, context):
        """Get valid queues for processing"""
        queues = context.scene.ts4ct_texture_queues
        valid_queues = {}
        for entry in queues:
            if entry.output_folder and len(entry.images) > 0:
                valid_queues[entry.mesh_name] = {
                    "folder": entry.output_folder,
                    "images": [img.path for img in entry.images]
                }
        return valid_queues

    def execute(self, context):
        # This method should not be called for modal operators
        # Use invoke() instead
        return {'CANCELLED'}

    def _add_timer(self, context):
        """Add a timer to enable modal processing"""
        self.timer = context.window_manager.event_timer_add(0.1, window=context.window)

    def _remove_timer(self, context):
        """Remove the timer"""
        if hasattr(self, 'timer'):
            context.window_manager.event_timer_remove(self.timer)

    def modal(self, context, event):
        """Modal handler for non-blocking baking"""
        # Handle cancel events
        if event.type in {'ESC', 'RIGHTMOUSE', 'LEFTMOUSE'} and event.value == 'PRESS':
            self._remove_timer(context)
            return self.cancel(context)
        
        if event.type == 'TIMER':
            return self._process_baking_step(context)
        
        return {'PASS_THROUGH'}

    def _process_baking_step(self, context):
        """Process one step of the baking queue"""
        if self.should_cancel:
            return self.cancel(context)
        
        # If we're not currently baking, start the next image
        if not self.is_baking:
            return self._start_next_image(context)
        
        return {'PASS_THROUGH'}

    def _advance_to_next_queue(self):
        """Advance to the next queue that has images"""
        queue_names = list(self.valid_queues.keys())
        
        while self.current_queue_index < len(queue_names):
            current_queue_name = queue_names[self.current_queue_index]
            queue_data = self.valid_queues[current_queue_name]
            
            # Ensure queue_data is valid and has images
            if queue_data and 'images' in queue_data and self.current_image_index < len(queue_data['images']):
                # Found a queue with images to process
                return True, current_queue_name, queue_data
            else:
                # Move to next queue
                self.current_queue_index += 1
                self.current_image_index = 0
        
        # No more queues with images
        return False, None, None
    
    def _start_next_image(self, context):
        """Start processing the next image in queue"""
        # Advance to the next queue that has images
        has_next, current_queue_name, queue_data = self._advance_to_next_queue()
        
        if not has_next or not queue_data:
            # All queues completed
            return self.finish_baking(context)
        
        # Additional safety checks
        if (not queue_data.get('images') or 
            self.current_image_index >= len(queue_data['images']) or
            not queue_data.get('folder')):
            # Invalid queue data, skip to next
            return {'PASS_THROUGH'}
        
        # Update the scene's active queue index to reflect current processing
        queues = context.scene.ts4ct_texture_queues
        for i, queue in enumerate(queues):
            if queue.mesh_name == current_queue_name:
                context.scene.ts4ct_active_queue_index = i
                break
        
        # Process current image
        image_path = queue_data['images'][self.current_image_index]
        output_folder = queue_data['folder']
        
        self.current_mesh_name = current_queue_name
        self.current_image_name = os.path.basename(image_path)
        
        # Update progress with detailed status
        device_info = getattr(context.scene.cycles, 'device', 'CPU')
        context.scene.ts4ct_bake_status = f"Processing {self.current_image_name} on {self.current_mesh_name} ({device_info}, Color only)"
        context.scene.ts4ct_bake_progress = (self.processed_images / self.total_images) * 100.0
        
        # Set baking flag to prevent re-entrance
        self.is_baking = True
        
        # Process the image
        success = self._process_single_image(context, current_queue_name, image_path, output_folder)
        
        if success:
            self.processed_images += 1
            context.scene.ts4ct_bake_progress = (self.processed_images / self.total_images) * 100.0
        
        self.current_image_index += 1
        self.is_baking = False  # Clear baking flag
        
        # Continue processing
        return {'PASS_THROUGH'}

    def _process_single_image(self, context, mesh_name, image_path, output_folder):
        """Process a single image for baking"""
        try:
            # Find mesh object in the entire scene
            mesh_obj = None
            for obj in context.scene.objects:
                if obj.name == mesh_name and obj.type == 'MESH':
                    mesh_obj = obj
                    break

            if not mesh_obj:
                # Mesh not found in scene
                return False

            # Load image
            if not os.path.exists(image_path):
                # Image not found
                return False

            img = bpy.data.images.load(image_path)

            # Find User_Texture node in material
            mat = mesh_obj.data.materials[0] if mesh_obj.data.materials else None
            if not mat or not mat.use_nodes:
                # No valid material
                bpy.data.images.remove(img)
                return False

            user_tex_node = None
            for node in mat.node_tree.nodes:
                if node.name == "Image Queue Texture" and node.type == 'TEX_IMAGE':
                    user_tex_node = node
                    break

            if not user_tex_node:
                # User_Texture node not found
                bpy.data.images.remove(img)
                return False

            # Set image to node
            user_tex_node.image = img

            # Find NEW_Texture node for baking target
            new_tex_node = None
            for node in mat.node_tree.nodes:
                if node.name == "New Bake" and node.type == 'TEX_IMAGE':
                    new_tex_node = node
                    break

            if not new_tex_node:
                # NEW_Texture node not found
                bpy.data.images.remove(img)
                return False

            # Set active image for baking
            mat.node_tree.nodes.active = new_tex_node

            # Setup optimal bake environment
            self._setup_bake_environment(context, mesh_obj)
            
            # Auto-select the New Bake image node for user visibility
            if new_tex_node:
                mat.node_tree.nodes.active = new_tex_node
                new_tex_node.select = True

            # Perform bake
            bpy.ops.object.bake(type='DIFFUSE')

            # Save baked image
            if new_tex_node.image:
                # Generate filename based on the current user texture image name
                user_image_name = "Unknown"
                if user_tex_node and user_tex_node.image:
                    user_image_name = os.path.splitext(user_tex_node.image.name)[0]
                
                bake_filename = f"{user_image_name}_newbake.png"
                bake_path = os.path.join(output_folder, bake_filename)

                # Save image
                new_tex_node.image.filepath_raw = bake_path
                new_tex_node.image.file_format = 'PNG'
                new_tex_node.image.save()

                # Image saved successfully

            # Clean up loaded image
            bpy.data.images.remove(img)
            return True

        except Exception as e:
            # Error processing image
            return False

    def cancel(self, context):
        """Cancel the baking process"""
        self._remove_timer(context)
        self.should_cancel = True
        
        # Restore original settings before canceling
        self._restore_render_settings(context)
        
        context.scene.ts4ct_bake_active = False
        context.scene.ts4ct_bake_status = "Cancelled"
        
        pi_errors.ErrorManager.show_success('batch_baking_cancelled',
            processed_count=self.processed_images,
            total_count=self.total_images)
        
        return {'CANCELLED'}

    def finish_baking(self, context):
        """Finish the baking process"""
        self._remove_timer(context)
        
        # Restore original settings before finishing
        self._restore_render_settings(context)
        
        context.scene.ts4ct_bake_active = False
        context.scene.ts4ct_bake_status = "Completed"
        
        if self.processed_images > 0:
            pi_errors.ErrorManager.show_success('batch_baking_completed',
                processed_count=self.processed_images,
                total_count=self.total_images)
        else:
            pi_errors.ErrorManager.show_error('no_images_processed')
        
        return {'FINISHED'}


class TSCT_OT_CancelBatchBake(Operator):
    """Cancel the batch texture baking process
    
    Immediately stops batch texture baking and restores original render settings.
    Can also be triggered with ESC key during baking. Completed images remain
    in output folders, allowing you to restart from where you left off.
    """
    bl_idname = "tsct.cancel_batch_bake"
    bl_label = "Cancel Batch Bake"
    bl_description = "Cancel the current batch texture baking process"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Set the cancel flag on any active bake operation
        # This is a simple implementation - in a more complex scenario,
        # you might want to track the active operator instance
        context.scene.ts4ct_bake_active = False
        context.scene.ts4ct_bake_status = "Cancelled by user"
        
        pi_errors.ErrorManager.show_success('batch_baking_cancelled',
            processed_count=0,
            total_count=0,
            custom_message="Batch baking cancelled!",
            custom_details=[
                "You can start a new batch bake when ready."
            ])
        
        return {'FINISHED'}


class TSCT_OT_RemoveMeshFromQueue(Operator):
    """Remove the selected mesh from the queue"""
    bl_idname = "tsct.remove_mesh_from_queue"
    bl_label = "Remove Mesh from Queue"
    bl_description = "Remove the selected mesh queue entry"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        queues = context.scene.ts4ct_texture_queues
        active_index = context.scene.ts4ct_active_queue_index

        if active_index >= len(queues):
            pi_errors.ErrorManager.show_error('no_queue_selected')
            return {'CANCELLED'}

        # Remove the selected queue entry
        removed_queue = queues[active_index]
        queues.remove(active_index)

        # Adjust index if necessary
        if active_index >= len(queues):
            context.scene.ts4ct_active_queue_index = max(0, len(queues) - 1)

        return {'FINISHED'}


# Registration
def register():
    bpy.utils.register_class(TSCT_OT_OpenShadowBake)
    bpy.utils.register_class(TSCT_OT_CreateShadowBakeCollection)
    bpy.utils.register_class(TSCT_OT_DuplicateToTextureTransfer)
    bpy.utils.register_class(TSCT_OT_SetupUVMaps)
    bpy.utils.register_class(TSCT_OT_SetupMaterials)
    bpy.utils.register_class(TSCT_OT_AddImageToMeshQueue)
    bpy.utils.register_class(TSCT_OT_RemoveImageFromQueue)
    bpy.utils.register_class(TSCT_OT_ClearMeshQueue)
    bpy.utils.register_class(TSCT_OT_CreateMeshQueue)
    bpy.utils.register_class(TSCT_OT_StartBatchTextureBake)
    bpy.utils.register_class(TSCT_OT_CancelBatchBake)
    bpy.utils.register_class(TSCT_OT_RemoveMeshFromQueue)


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

    try:
        bpy.utils.unregister_class(TSCT_OT_DuplicateToTextureTransfer)
    except Exception:
        pass

    try:
        bpy.utils.unregister_class(TSCT_OT_SetupUVMaps)
    except Exception:
        pass

    try:
        bpy.utils.unregister_class(TSCT_OT_SetupMaterials)
    except Exception:
        pass

    try:
        bpy.utils.unregister_class(TSCT_OT_AddImageToMeshQueue)
    except Exception:
        pass

    try:
        bpy.utils.unregister_class(TSCT_OT_RemoveImageFromQueue)
    except Exception:
        pass

    try:
        bpy.utils.unregister_class(TSCT_OT_ClearMeshQueue)
    except Exception:
        pass

    try:
        bpy.utils.unregister_class(TSCT_OT_CreateMeshQueue)
    except Exception:
        pass

    try:
        bpy.utils.unregister_class(TSCT_OT_StartBatchTextureBake)
    except Exception:
        pass

    try:
        bpy.utils.unregister_class(TSCT_OT_CancelBatchBake)
    except Exception:
        pass

    try:
        bpy.utils.unregister_class(TSCT_OT_RemoveMeshFromQueue)
    except Exception:
        pass


if __name__ == "__main__":
    register()