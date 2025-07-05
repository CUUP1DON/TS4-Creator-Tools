import bpy
from bpy.props import IntProperty
from bpy.types import Operator

def s4studio_not_found(self, context):
    self.layout.label(text="S4Studio Mesh Tools addon not found or not enabled.")

def s4studio_properties_not_found(self, context):
    self.layout.label(text="S4Studio properties not found on selected mesh(es).")

def no_mesh_selected(self, context):
    self.layout.label(text="No mesh objects selected.")

def cut_number_set_success(self, context):
    cut_num = context.scene.get('temp_cut_number', 0)
    count = context.scene.get('temp_success_count', 0)
    self.layout.label(text=f"Set cut number {cut_num} for {count} mesh(es)")

def display_popup_list(popups):
    def draw(self, context):
        layout = self.layout
        for popup in popups:
            popup(self, context)
    return draw

class OBJECT_OT_s4studio_set_cut_number(Operator):
    """Set cut number for selected mesh objects"""
    bl_idname = "object.s4studio_set_cut_number"
    bl_label = "Set Cut Number"
    bl_options = {'REGISTER', 'UNDO'}
    
    cut_number: IntProperty(
        name="Cut Number",
        description="Cut number to assign to selected meshes",
        default=0,
        min=0
    )
    
    def execute(self, context):
        selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']
        
        if not selected_objects:
            bpy.context.window_manager.popup_menu(no_mesh_selected, title="Creator Tools", icon='ERROR')
            return {'CANCELLED'}
        
        # Try to set cut numbers directly, check for S4Studio during the process
        success_count = 0
        s4studio_found = False
        
        for obj in selected_objects:
            try:
                # Access the s4studio property group on the mesh data
                if hasattr(obj.data, 's4studio'):
                    obj.data.s4studio.cut = str(self.cut_number)
                    success_count += 1
                    s4studio_found = True
            except Exception as e:
                print(f"Error setting cut number for {obj.name}: {str(e)}")
        
        # Show results via popup
        if success_count > 0:
            # Store values temporarily for the popup
            context.scene['temp_cut_number'] = self.cut_number
            context.scene['temp_success_count'] = success_count
            bpy.context.window_manager.popup_menu(cut_number_set_success, title="Creator Tools", icon='CHECKMARK')
            # Clean up temporary values
            del context.scene['temp_cut_number']
            del context.scene['temp_success_count']
        elif not s4studio_found:
            bpy.context.window_manager.popup_menu(s4studio_not_found, title="Creator Tools", icon='ERROR')
        else:
            bpy.context.window_manager.popup_menu(s4studio_properties_not_found, title="Creator Tools", icon='ERROR')
        
        return {'FINISHED'}
    
    def check_s4studio_addon(self):
        """Check if S4Studio addon is enabled and properties are available"""
        # Method 1: Check if the s4studio property exists on mesh data
        try:
            # Create a temporary mesh to test
            temp_mesh = bpy.data.meshes.new("temp_test")
            has_s4studio = hasattr(temp_mesh, 's4studio')
            bpy.data.meshes.remove(temp_mesh)
            if has_s4studio:
                return True
        except:
            pass
        
        # Method 2: Check enabled addons with different patterns
        enabled_addons = bpy.context.preferences.addons
        addon_patterns = [
            's4studio', 
            'sims 4 studio', 
            'sims4studio',
            'blender_library',
            'mesh_tools'
        ]
        
        for addon in enabled_addons:
            addon_name = addon.module.lower()
            for pattern in addon_patterns:
                if pattern in addon_name:
                    return True
        
        # Method 3: Check if we can access s4studio properties on existing mesh
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH' and hasattr(obj.data, 's4studio'):
                return True
        
        return False
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

def register():
    bpy.utils.register_class(OBJECT_OT_s4studio_set_cut_number)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_s4studio_set_cut_number)