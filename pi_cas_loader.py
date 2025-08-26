import bpy
import os
from bpy.types import Operator

class TSCT_OT_load_cas(Operator):
    bl_idname = "object.load_cas"
    bl_label = "Load a CAS Part"
    bl_description = "Load a CAS Part"
    bl_options = {'REGISTER', 'UNDO'}
    
    body_type: bpy.props.EnumProperty(
        name="Body Type",
        description="Body type for CAS item",
        items=[
            ('AM', 'Adult Male', 'Adult Male body type'),
            ('AF', 'Adult Female', 'Adult Female body type'),
            ('C', 'Child', 'Child body type'),
            ('T', 'Toddler', 'Toddler body type'),
            ('I', 'Infant', 'Infant body type'),
        ],
        default='AM'
    )
    
    cas_item: bpy.props.EnumProperty(
        name="CAS Item",
        description="CAS item to load",
        items=[
            ('Dress', 'Dress', 'Dress clothing item'),
            ('Pants', 'Pants', 'Pants clothing item'),
            ('Shirt', 'Shirt', 'Shirt clothing item'),
            ('Skirt', 'Skirt', 'Skirt clothing item')
        ],
        default='Dress'
    )
    
    def get_length_items(self, context):
        """Dynamic length items based on selected CAS item and body type"""
        if self.cas_item == 'Dress':
            if self.body_type == 'I':  # Infant - only one dress length
                return [('', 'Default', 'Default dress length')]
            elif self.body_type == 'T':  # Toddler - Med and Long only
                return [
                    ('Med', 'Medium', 'Medium length dress'),
                    ('Long', 'Long', 'Long length dress')
                ]
            else:  # Adults and Children - all three lengths
                return [
                    ('Long', 'Long', 'Long length dress'),
                    ('Med', 'Medium', 'Medium length dress'),
                    ('Short', 'Short', 'Short length dress')
                ]
        elif self.cas_item == 'Skirt':
            if self.body_type == 'I':  # Infant - only one skirt length
                return [('', 'Default', 'Default skirt length')]
            elif self.body_type == 'T':  # Toddler - only one skirt length
                return [('', 'Default', 'Default skirt length')]
            else:  # Adults and Children - all three lengths
                return [
                    ('Long', 'Long', 'Long length skirt'),
                    ('Med', 'Medium', 'Medium length skirt'),
                    ('Short', 'Short', 'Short length skirt')
                ]
        elif self.cas_item == 'Pants':
            return [
                ('Pants', 'Pants', 'Full length pants'),
                ('Shorts', 'Shorts', 'Short pants')
            ]
        elif self.cas_item == 'Shirt':
            return [
                ('LongSleeve', 'Long Sleeve', 'Long sleeve shirt'),
                ('ShortSleeve', 'Short Sleeve', 'Short sleeve shirt')
            ]
        else:
            return [('', 'Default', 'Default length')]
    
    length: bpy.props.EnumProperty(
        name="Length/Style",
        description="Length or style variation of the CAS item",
        items=get_length_items
    )
    
    def invoke(self, context, event):
        # Force the dialog to appear
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "body_type")
        layout.prop(self, "cas_item")
        
        # Only show length dropdown if there are multiple options
        length_items = self.get_length_items(context)
        if len(length_items) > 1:
            layout.prop(self, "length")
    
    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Load a CAS Part")
        
        # Get the addon directory
        addon_dir = os.path.dirname(os.path.realpath(__file__))
        assets_dir = os.path.join(addon_dir, "assets")
        cas_dir = os.path.join(assets_dir, "cas")
        dress_dir = os.path.join(cas_dir, "dress")
        pants_dir = os.path.join(cas_dir, "pants")
        shirt_dir = os.path.join(cas_dir, "shirt")
        skirt_dir = os.path.join(cas_dir, "skirt")
        
        # Construct the blend file name based on body type and CAS item
        blend_file = self.get_blend_filename()
        
        # Determine which directory to use based on CAS item type
        if self.cas_item == 'Dress':
            blend_path = os.path.join(dress_dir, blend_file)
            search_location = "dress folder"
            fallback_dir = dress_dir
        elif self.cas_item == 'Pants':
            blend_path = os.path.join(pants_dir, blend_file)
            search_location = "pants folder"
            fallback_dir = pants_dir
        elif self.cas_item == 'Shirt':
            blend_path = os.path.join(shirt_dir, blend_file)
            search_location = "shirt folder"
            fallback_dir = shirt_dir
        else:  # Skirt
            blend_path = os.path.join(skirt_dir, blend_file)
            search_location = "skirt folder"
            fallback_dir = skirt_dir
        
        # Check if file exists
        if not os.path.exists(blend_path):
            # Try assets folder as fallback for organized CAS item types
            if fallback_dir is not None:
                fallback_path = os.path.join(assets_dir, blend_file)
                if os.path.exists(fallback_path):
                    blend_path = fallback_path
                    search_location = "assets folder (fallback)"
                else:
                    self.display_popup_error(f"CAS item file not found: {blend_file}\nSearched in: {search_location} and assets folder")
                    return {'CANCELLED'}
            else:
                self.display_popup_error(f"CAS item file not found: {blend_file}\nSearched in: {search_location}")
                return {'CANCELLED'}
        
        print(f"Loading {blend_file} from {search_location}: {blend_path}")
        
        # Load the blend file
        try:
            with bpy.data.libraries.load(blend_path) as (data_from, data_to):
                # Debug: Print all available objects
                print(f"Available objects in {blend_file}: {list(data_from.objects)}")
                
                # Look for objects that match the expected naming pattern
                expected_object_name = self.get_expected_object_name()
                target_objects = [name for name in data_from.objects if expected_object_name in name]
                
                # If no exact match, try loading all objects from the file
                if not target_objects:
                    print(f"No objects found with name containing '{expected_object_name}', loading all objects")
                    target_objects = data_from.objects
                
                data_to.objects = target_objects
                data_to.materials = data_from.materials
            
            # Add loaded objects to the scene
            loaded_objects = []
            for obj in data_to.objects:
                if obj is not None:
                    context.collection.objects.link(obj)
                    obj.select_set(True)
                    loaded_objects.append(obj)
            
            if loaded_objects:
                context.view_layer.objects.active = loaded_objects[0]
                body_type_name = dict(self.body_type_items)[self.body_type]
                cas_item_name = dict(self.cas_item_items)[self.cas_item]
                length_name = self.get_length_display_name()
                self.display_popup_success(f"{body_type_name} {cas_item_name} {length_name} CAS item loaded successfully. Loaded {len(loaded_objects)} objects.")
            else:
                self.display_popup_error("No objects were loaded from the file.")
                return {'CANCELLED'}
            
            return {'FINISHED'}
            
        except Exception as e:
            self.display_popup_error(f"Error loading CAS item: {str(e)}")
            return {'CANCELLED'}
    
    def get_blend_filename(self):
        """Generate the blend file name based on body type, CAS item, and length"""
        if self.cas_item in ['Dress', 'Skirt']:
            if self.body_type == 'I' or (self.body_type == 'T' and self.cas_item == 'Skirt'):  # Infant or Toddler Skirt - body type + item name
                return f"{self.body_type}_{self.cas_item}.blend"
            else:  # All other body types include length
                return f"{self.body_type}_{self.cas_item}{self.length}.blend"
        elif self.cas_item == 'Pants':
            if self.length == 'Shorts':
                return f"{self.body_type}_Shorts.blend"
            else:
                return f"{self.body_type}_Pants.blend"
        elif self.cas_item == 'Shirt':
            if self.length:  # Only add length if it's not empty
                return f"{self.body_type}_{self.length}.blend"
            else:
                return f"{self.body_type}_{self.cas_item}.blend"
        else:
            return f"{self.body_type}_{self.cas_item}.blend"
    
    def get_expected_object_name(self):
        """Generate the expected object name for loading"""
        if self.cas_item in ['Dress', 'Skirt']:
            if self.body_type == 'I' or (self.body_type == 'T' and self.cas_item == 'Skirt'):  # Infant or Toddler Skirt
                return f"{self.body_type}_{self.cas_item}"
            else:
                return f"{self.body_type}_{self.cas_item}{self.length}"
        elif self.cas_item == 'Pants':
            if self.length == 'Shorts':
                return f"{self.body_type}_Shorts"
            else:
                return f"{self.body_type}_Pants"
        elif self.cas_item == 'Shirt':
            if self.length:  # Only add length if it's not empty
                return f"{self.body_type}_{self.length}"
            else:
                return f"{self.body_type}_{self.cas_item}"
        else:
            return f"{self.body_type}_{self.cas_item}"
    
    def get_length_display_name(self):
        """Get display name for the length/style for success message"""
        length_items = self.get_length_items(None)
        for item in length_items:
            if item[0] == self.length:
                return item[1]
        return ""
    
    @property
    def body_type_items(self):
        return [
            ('AM', 'Adult Male'),
            ('AF', 'Adult Female'),
            ('C', 'Child'),
            ('T', 'Toddler'),
            ('I', 'Infant'),
        ]
    
    @property
    def cas_item_items(self):
        return [
            ('Dress', 'Dress'),
            ('Pants', 'Pants'),
            ('Shirt', 'Shirt'),
            ('Skirt', 'Skirt'),
        ]
    
    def display_popup_error(self, message):
        def popup(self, context):
            self.layout.label(text=message)
        bpy.context.window_manager.popup_menu(popup, title="Creator Tools", icon='ERROR')
    
    def display_popup_success(self, message):
        def popup(self, context):
            self.layout.label(text=message)
        bpy.context.window_manager.popup_menu(popup, title="Creator Tools", icon='INFO')

# Register and unregister functions
def register():
    bpy.utils.register_class(TSCT_OT_load_cas)

def unregister():
    bpy.utils.unregister_class(TSCT_OT_load_cas)