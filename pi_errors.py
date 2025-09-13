"""
Centralized Error and Message Management for TS4 Creator Tools
Provides user-friendly error messages and consistent popup handling across the addon.
"""

import bpy

class ErrorManager:
    """Centralized error and message handling for TS4 Creator Tools"""
    
    # Message categories
    SELECTION = "selection"
    FILE = "file"  
    CONTEXT = "context"
    VALIDATION = "validation"
    PROCESS = "process"
    SUCCESS = "success"
    
    # Centralized message definitions with user-friendly content
    MESSAGES = {
        
        # === SELECTION ERRORS ===
        "no_object_selected": {
            "category": SELECTION,
            "title": "No Object Selected",
            "message": "Please select an object to continue.",
            "details": [
                "Select the object you want to work with",
                "Make sure objects are visible in the viewport",
                "Check the Outliner if objects seem missing"
            ],
            "icon": "ERROR"
        },
        
        "no_mesh_selected": {
            "category": SELECTION, 
            "title": "No Mesh Selected",
            "message": "Please select a mesh object to continue.",
            "details": [
                "Only mesh objects can be used for this operation",
                "Select a mesh from the 3D viewport or Outliner",
                "Make sure the selected object is a mesh type"
            ],
            "icon": "ERROR"
        },
        
        "wrong_object_type": {
            "category": SELECTION,
            "title": "Wrong Object Type", 
            "message": "Selected object is not a mesh.",
            "details": [
                "This tool only works with mesh objects",
                "Select a different object or convert to mesh"
            ],
            "icon": "ERROR"
        },
        
        # === FILE ERRORS ===
        "file_not_found": {
            "category": FILE,
            "title": "File Not Found",
            "message": "The requested file could not be found.",
            "details": [
                "Check that the file path is correct",
                "Verify the file exists in the expected location",
                "Try reinstalling the addon if using built-in assets"
            ],
            "icon": "ERROR"
        },
        
        "asset_file_missing": {
            "category": FILE,
            "title": "Asset File Missing",
            "message": "The asset file is missing from the addon.",
            "details": [
                "This usually means the addon installation is incomplete",
                "Try reinstalling the TS4 Creator Tools addon",
                "Contact support if the problem persists"
            ],
            "icon": "ERROR"
        },
        
        "custom_asset_not_found": {
            "category": FILE,
            "title": "Custom Asset Not Found", 
            "message": "Could not find the requested custom asset.",
            "details": [
                "Check that the file exists in your custom assets folder",
                "Verify the file name and extension are correct",
                "Make sure custom asset paths are set up properly"
            ],
            "icon": "ERROR"
        },
        
        # === CONTEXT ERRORS ===
        "wrong_mode": {
            "category": CONTEXT,
            "title": "Wrong Mode",
            "message": "This operation requires a different mode.",
            "details": [
                "Switch to the appropriate mode (Object/Edit)",
                "Some tools only work in specific modes"
            ],
            "icon": "ERROR"
        },
        
        "exit_edit_mode": {
            "category": CONTEXT,
            "title": "Exit Edit Mode",
            "message": "Please exit Edit Mode first.",
            "details": [
                "Press Tab to switch to Object Mode",
                "This operation requires Object Mode"
            ],
            "icon": "ERROR"
        },
        
        "no_rig_found": {
            "category": CONTEXT,
            "title": "No Rig Found",
            "message": "Cannot find a rig in your scene.",
            "details": [
                "Load a rig using the 'Load Rig' button first",
                "Make sure the rig is visible and not hidden",
                "Check that you have an armature object in your scene"
            ],
            "icon": "ERROR"
        },
        
        "rig_not_found": {
            "category": CONTEXT,
            "title": "No Rig Found",
            "message": "No armature containing 'rig' found in scene.",
            "details": [
                "Import a rig file first using the 'Load Rig' button",
                "Make sure your armature has 'rig' in its name",
                "Check that the rig object is not hidden"
            ],
            "icon": "ERROR"
        },
        
        "rig_target_meshes_not_found": {
            "category": CONTEXT,
            "title": "Target Meshes Not Found",
            "message": "Target mesh objects could not be found.",
            "details": [
                "This is an internal error with mesh selection",
                "Try selecting your meshes again",
                "Restart the rig linking process"
            ],
            "icon": "ERROR"
        },
        
        "rig_valid_meshes_not_found": {
            "category": CONTEXT,
            "title": "No Valid Meshes Found",
            "message": "No valid target mesh objects found.",
            "details": [
                "Make sure the selected objects still exist",
                "Check that objects haven't been deleted",
                "Try reselecting your mesh objects"
            ],
            "icon": "ERROR"
        },
        
        "selected_rig_not_found": {
            "category": CONTEXT,
            "title": "Selected Rig Not Found",
            "message": "The selected rig could not be found.",
            "details": [
                "The rig may have been deleted or renamed",
                "Try refreshing the rig list",
                "Make sure the rig still exists in the scene"
            ],
            "icon": "ERROR"
        },
        
        # === VALIDATION ERRORS ===
        "no_weight_groups": {
            "category": VALIDATION,
            "title": "No Vertex Groups",
            "message": "The selected object has no vertex groups for weight transfer.",
            "details": [
                "The source object needs vertex groups to transfer weights",
                "Make sure you selected the right object",
                "Check that the object has been properly rigged"
            ],
            "icon": "ERROR"
        },
        
        "invalid_mesh_data": {
            "category": VALIDATION,
            "title": "Invalid Mesh Data",
            "message": "The mesh data appears to be corrupt or invalid.",
            "details": [
                "Try reloading the object or file",
                "The mesh may have been corrupted",
                "Consider using a backup version"
            ],
            "icon": "ERROR"
        },
        
        "topology_mismatch": {
            "category": VALIDATION,
            "title": "Topology Mismatch",
            "message": "The meshes have different topology.",
            "details": [
                "Both meshes need the same number of vertices and faces",
                "Make sure you're using compatible mesh versions",
                "Consider using a different transfer method"
            ],
            "icon": "ERROR"
        },
        
        "no_marked_vertices": {
            "category": VALIDATION,
            "title": "No Vertices Marked",
            "message": "No vertices have been marked for this operation.",
            "details": [
                "Enter Edit Mode and select vertices first",
                "Use the 'Mark LOD Vertices' button to mark them",
                "Make sure you have vertices selected"
            ],
            "icon": "ERROR"
        },
        
        "validation_error": {
            "category": VALIDATION,
            "title": "Validation Error",
            "message": "A validation check failed.",
            "details": [
                "Please check the requirements for this operation",
                "Make sure all needed objects and data are present"
            ],
            "icon": "ERROR"
        },
        
        # === PROCESS ERRORS ===
        "operation_failed": {
            "category": PROCESS,
            "title": "Operation Failed", 
            "message": "The operation could not be completed.",
            "details": [
                "An unexpected error occurred",
                "Try the operation again",
                "Check that all requirements are met"
            ],
            "icon": "ERROR"
        },
        
        "connection_failed": {
            "category": PROCESS,
            "title": "Connection Failed",
            "message": "Could not connect vertices to target objects.",
            "details": [
                "Make sure target objects are close enough",
                "Check that vertices are properly marked",
                "Verify that target objects exist and are visible"
            ],
            "icon": "ERROR"
        },
        
        "blender_context_error": {
            "category": PROCESS,
            "title": "Blender Context Error",
            "message": "Blender is not in the right state for this operation.",
            "details": [
                "Try switching modes or refreshing the interface",
                "Some operations require specific Blender states",
                "Restart Blender if problems persist"
            ],
            "icon": "ERROR"
        },
        
        # === SUCCESS MESSAGES ===
        "operation_complete": {
            "category": SUCCESS,
            "title": "Operation Complete",
            "message": "The operation completed successfully!",
            "details": [],
            "icon": "CHECKMARK"
        },
        
        "weights_transferred": {
            "category": SUCCESS,
            "title": "Weights Transferred",
            "message": "Vertex weights have been transferred successfully.",
            "details": [
                "REF mesh has been removed as it's no longer needed",
                "Your mesh now has proper weight painting"
            ],
            "icon": "CHECKMARK"
        },
        
        "mesh_subdivided": {
            "category": SUCCESS,
            "title": "Mesh Subdivided",
            "message": "REF mesh has been subdivided successfully.",
            "details": [
                "The mesh now has more geometry for detailed work"
            ],
            "icon": "CHECKMARK"
        },
        
        "weights_smoothed": {
            "category": SUCCESS,
            "title": "Weights Smoothed", 
            "message": "Vertex weights have been smoothed.",
            "details": [
                "Weight transitions should now be smoother",
                "This helps prevent harsh deformation boundaries"
            ],
            "icon": "CHECKMARK"
        },
        
        "weights_limited": {
            "category": SUCCESS,
            "title": "Weights Limited",
            "message": "Limited the number of weights per vertex.",
            "details": [
                "Each vertex now influences a maximum number of bones",
                "This improves performance and prevents deformation issues"
            ],
            "icon": "CHECKMARK"  
        },
        
        "doubles_removed": {
            "category": SUCCESS,
            "title": "Duplicates Removed",
            "message": "Duplicate vertices have been merged.",
            "details": [
                "This cleaned up overlapping geometry",
                "Your mesh should now be cleaner"
            ],
            "icon": "CHECKMARK"
        },
        
        "faces_converted": {
            "category": SUCCESS,
            "title": "Faces Converted",
            "message": "Face topology has been changed successfully.",
            "details": [
                "Mesh faces have been converted as requested"
            ],
            "icon": "CHECKMARK"
        },
        
        "rig_linked": {
            "category": SUCCESS,
            "title": "Rig Linked",
            "message": "Rig has been linked to your meshes.",
            "details": [
                "Your meshes are now connected to the armature",
                "You can now pose and animate your character"
            ],
            "icon": "CHECKMARK"
        },
        
        "vertex_color_applied": {
            "category": SUCCESS,
            "title": "Vertex Color Applied",
            "message": "Vertex colors have been applied successfully.",
            "details": [
                "The vertex color affects how the mesh behaves in-game"
            ],
            "icon": "CHECKMARK"
        },
        
        "uv_setup_complete": {
            "category": SUCCESS,
            "title": "UV Setup Complete",
            "message": "UV maps have been set up correctly.",
            "details": [
                "Your mesh is now ready for texturing",
                "Make sure to unwrap your UVs if needed"
            ],
            "icon": "CHECKMARK"
        },
        
        "lod_created": {
            "category": SUCCESS,
            "title": "LOD Levels Created",
            "message": "Level of Detail meshes have been generated.",
            "details": [
                "All LODs have been placed in the LOD Collection",
                "These optimize performance at different distances"
            ],
            "icon": "CHECKMARK"
        },
        
        "vertices_connected": {
            "category": SUCCESS,
            "title": "Vertices Connected",
            "message": "Vertices have been connected successfully.",
            "details": [
                "Marked vertices are now positioned properly",
                "This helps create seamless connections between parts"
            ],
            "icon": "CHECKMARK"
        },
        
        "collection_created": {
            "category": SUCCESS,
            "title": "Collection Created", 
            "message": "Baking collection has been created.",
            "details": [
                "Add your meshes to this collection before baking",
                "This organizes your assets for shadow map creation"
            ],
            "icon": "CHECKMARK"
        },
        
        "bake_file_opened": {
            "category": SUCCESS,
            "title": "Bake File Opened",
            "message": "Shadow bake file has been opened in a new window.",
            "details": [
                "The baking setup is ready to use",
                "Your meshes have been imported automatically"
            ],
            "icon": "CHECKMARK"
        },
        
        "rig_linked_single": {
            "category": SUCCESS,
            "title": "Rig Linked",
            "message": "Mesh successfully linked to rig.",
            "details": [
                "Your mesh is now connected to the armature",
                "You can now pose and animate your character",
                "The armature modifier has been applied"
            ],
            "icon": "CHECKMARK"
        },
        
        "rig_linked_multiple": {
            "category": SUCCESS,
            "title": "Multiple Meshes Linked",
            "message": "{count} meshes successfully linked to rig.",
            "details": [
                "All selected meshes are now connected to the armature",
                "You can now pose and animate your character",
                "Armature modifiers have been applied to all meshes"
            ],
            "icon": "CHECKMARK"
        },
        
        "rig_link_partial_failure": {
            "category": PROCESS,
            "title": "Partial Rig Link Failure",
            "message": "{success} meshes linked successfully, {failed} failed.",
            "details": [
                "Some meshes could not be linked to the rig",
                "This may be due to invalid mesh data or context issues",
                "Try linking the failed meshes individually"
            ],
            "icon": "ERROR"
        },
    }
    
    @staticmethod
    def show_popup(message_key, **kwargs):
        """
        Show a detailed popup message.
        
        Args:
            message_key: Key from MESSAGES dictionary
            **kwargs: Additional parameters for message formatting
                - custom_message: Override the default message
                - custom_details: Override the default details list
                - count: For messages that show counts
                - name: For messages that show object names
                - file_path: For file-related messages
        """
        if message_key not in ErrorManager.MESSAGES:
            # Fallback for unknown message keys
            def fallback_popup(self, context):
                self.layout.label(text=f"Unknown message: {message_key}")
            bpy.context.window_manager.popup_menu(fallback_popup, title="Creator Tools", icon='ERROR')
            return
            
        msg_data = ErrorManager.MESSAGES[message_key]
        
        def popup_display(self, context):
            layout = self.layout
            
            # Main message
            main_message = kwargs.get('custom_message', msg_data['message'])
            if 'count' in kwargs and '{count}' in main_message:
                main_message = main_message.format(count=kwargs['count'])
            if 'name' in kwargs and '{name}' in main_message:
                main_message = main_message.format(name=kwargs['name'])
            if 'file_path' in kwargs and '{file_path}' in main_message:
                main_message = main_message.format(file_path=kwargs['file_path'])
                
            layout.label(text=main_message)
            
            # Details section
            details = kwargs.get('custom_details', msg_data.get('details', []))
            if details:
                layout.separator()
                for detail in details:
                    layout.label(text=f"• {detail}")
                    
            # Additional custom info
            if 'additional_info' in kwargs:
                layout.separator()
                for info in kwargs['additional_info']:
                    layout.label(text=info)
        
        icon = msg_data.get('icon', 'INFO')
        title = kwargs.get('title', 'Creator Tools')
        bpy.context.window_manager.popup_menu(popup_display, title=title, icon=icon)
    
    @staticmethod
    def report(operator, message_key, report_type='INFO', **kwargs):
        """
        Use operator.report() for simple messages.
        
        Args:
            operator: The calling operator instance
            message_key: Key from MESSAGES dictionary  
            report_type: 'INFO', 'WARNING', 'ERROR'
            **kwargs: Additional parameters for message formatting
        """
        if message_key not in ErrorManager.MESSAGES:
            operator.report({'ERROR'}, f"Unknown message: {message_key}")
            return
            
        msg_data = ErrorManager.MESSAGES[message_key]
        message = kwargs.get('custom_message', msg_data['message'])
        
        # Format message with provided parameters
        if 'count' in kwargs and '{count}' in message:
            message = message.format(count=kwargs['count'])
        if 'name' in kwargs and '{name}' in message:
            message = message.format(name=kwargs['name'])
        if 'file_path' in kwargs and '{file_path}' in message:
            message = message.format(file_path=kwargs['file_path'])
            
        operator.report({report_type}, message)

    @staticmethod
    def show_error(error_key, **kwargs):
        """Convenience method for showing error popups"""
        ErrorManager.show_popup(error_key, **kwargs)
    
    @staticmethod
    def show_success(success_key, **kwargs):
        """Convenience method for showing success popups"""
        ErrorManager.show_popup(success_key, **kwargs)

# Convenience functions for common error patterns
def show_no_object_selected():
    """Show 'no object selected' error"""
    ErrorManager.show_error('no_object_selected')

def show_no_mesh_selected():
    """Show 'no mesh selected' error"""
    ErrorManager.show_error('no_mesh_selected')

def show_wrong_mode():
    """Show 'wrong mode' error"""
    ErrorManager.show_error('wrong_mode')

def show_exit_edit_mode():
    """Show 'exit edit mode' error"""
    ErrorManager.show_error('exit_edit_mode')

def show_file_not_found(file_path=""):
    """Show 'file not found' error"""
    ErrorManager.show_error('file_not_found', 
                           custom_details=[f"File: {file_path}"] if file_path else None)

def show_no_rig_found():
    """Show 'no rig found' error"""
    ErrorManager.show_error('no_rig_found')

def show_operation_complete():
    """Show 'operation complete' success"""
    ErrorManager.show_success('operation_complete')

def show_weights_transferred():
    """Show 'weights transferred' success"""
    ErrorManager.show_success('weights_transferred')

def show_vertex_color_applied(count=1, color_type=""):
    """Show vertex color applied success"""
    message = f"Applied {color_type} vertex color to {count} object(s)." if color_type else f"Applied vertex color to {count} object(s)."
    ErrorManager.show_success('vertex_color_applied', custom_message=message)

# Legacy support functions for gradual migration
def display_popup_list(popup_functions):
    """
    Legacy support function for existing popup lists.
    This allows gradual migration from old popup system.
    """
    def draw(self, context):
        layout = self.layout
        for popup_func in popup_functions:
            if callable(popup_func):
                popup_func(self, context)
            else:
                layout.label(text=str(popup_func))
    return draw