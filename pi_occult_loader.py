import bpy
import os
from bpy.types import Operator
from .ci_asset_management import show_popup

class TSCT_OT_load_occult(Operator):
    bl_idname = "object.load_occult"
    bl_label = "Load an Occult Item"
    bl_description = "Load an Occult Item"
    bl_options = {'REGISTER', 'UNDO'}

    occult_type: bpy.props.EnumProperty(
        name="Occult Type",
        description="Type of occult item",
        items=[
            ('Fairy', 'Fairy', 'Fairy (wings)'),
            ('F_Mermaid', 'Female Mermaid', 'Female Mermaid'),
            ('M_Merman', 'Male Merman', 'Male Merman'),
            ('F_Werewolf', 'Female Werewolf', 'Female Werewolf'),
            ('M_Werewolf', 'Male Werewolf', 'Male Werewolf'),
        ],
        default='Fairy'
    )

    def get_mesh_type_items(self, context):
        """Dynamically generate mesh type options based on occult type"""
        if self.occult_type == 'Fairy':
            return [
                ('Big', 'Wings Big', 'Big wings'),
                ('Med', 'Wings Med', 'Medium wings'),
                ('Small', 'Wings Small', 'Small wings'),
            ]
        elif self.occult_type == 'F_Mermaid':
            return [
                ('Tail', 'Tail', 'Female Mermaid tail'),
            ]
        elif self.occult_type == 'M_Merman':
            return [
                ('Tail', 'Tail', 'Male Merman tail'),
            ]
        elif self.occult_type == 'F_Werewolf':
            return [
                ('Head', 'Head', 'Female Werewolf head'),
                ('Top', 'Top', 'Female Werewolf top'),
                ('Bottom', 'Bottom', 'Female Werewolf bottom'),
                ('Feet', 'Feet', 'Female Werewolf feet'),
            ]
        elif self.occult_type == 'M_Werewolf':
            return [
                ('Head', 'Head', 'Male Werewolf head'),
                ('Top', 'Top', 'Male Werewolf top'),
                ('Bottom', 'Bottom', 'Male Werewolf bottom'),
                ('Feet', 'Feet', 'Male Werewolf feet'),
            ]
        return [('NONE', 'None', 'No items available')]

    mesh_type: bpy.props.EnumProperty(
        name="Mesh Type",
        description="Type of mesh to load",
        items=get_mesh_type_items
    )

    def invoke(self, context, event):
        # Force the dialog to appear
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "occult_type")
        layout.prop(self, "mesh_type")

    def execute(self, context):
        bpy.ops.ed.undo_push(message="Creator Tools: Load an Occult Item")

        # Get the addon directory
        addon_dir = os.path.dirname(os.path.realpath(__file__))
        assets_dir = os.path.join(addon_dir, "assets")
        occult_dir = os.path.join(assets_dir, "occult")

        # Set up subdirectories matching body base loader structure
        fairy_dir = os.path.join(occult_dir, "fairy")
        mermaid_dir = os.path.join(occult_dir, "mermaid")
        werewolf_dir = os.path.join(occult_dir, "werewolf")

        # Construct the blend file path based on occult type and mesh type
        # Special handling for Fairy which uses Wings_ prefix
        if self.occult_type == 'Fairy':
            blend_file = f"Wings_{self.mesh_type}.blend"
            blend_path = os.path.join(fairy_dir, blend_file)
            search_location = "occult/fairy folder"
            fallback_dir = fairy_dir
        # Mermaid and Werewolf follow the pattern: {occult_type}_{mesh_type}.blend
        elif self.occult_type in ['F_Mermaid', 'M_Merman']:
            blend_file = f"{self.occult_type}_{self.mesh_type}.blend"
            blend_path = os.path.join(mermaid_dir, blend_file)
            search_location = "occult/mermaid folder"
            fallback_dir = mermaid_dir
        elif self.occult_type in ['F_Werewolf', 'M_Werewolf']:
            # Convert to match file naming: F_Werewolf -> AF_Werewolf, M_Werewolf -> AM_Werewolf
            file_prefix = f"A{self.occult_type}"
            blend_file = f"{file_prefix}_{self.mesh_type}.blend"
            blend_path = os.path.join(werewolf_dir, blend_file)
            search_location = "occult/werewolf folder"
            fallback_dir = werewolf_dir
        else:
            blend_file = f"{self.occult_type}_{self.mesh_type}.blend"
            blend_path = os.path.join(occult_dir, blend_file)
            search_location = "occult folder"
            fallback_dir = None

        # Check if file exists
        if not os.path.exists(blend_path):
            # Try assets folder as fallback
            if fallback_dir is not None:
                fallback_path = os.path.join(assets_dir, blend_file)
                if os.path.exists(fallback_path):
                    blend_path = fallback_path
                    search_location = "assets folder (fallback)"
                else:
                    show_popup(f"Occult item file not found: {blend_file}\nSearched in: {search_location} and assets folder", icon='ERROR')
                    return {'CANCELLED'}
            else:
                show_popup(f"Occult item file not found: {blend_file}\nSearched in: {search_location}", icon='ERROR')
                return {'CANCELLED'}

        print(f"Loading {blend_file} from {search_location}: {blend_path}")

        # Load the blend file
        try:
            with bpy.data.libraries.load(blend_path) as (data_from, data_to):
                # Debug: Print all available objects
                print(f"Available objects in {blend_file}: {list(data_from.objects)}")

                # Load all objects from the file
                data_to.objects = data_from.objects
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
                occult_type_name = dict(self.occult_type_items)[self.occult_type]
                mesh_type_name = dict(self.mesh_type_items)[self.mesh_type]
                show_popup(f"{occult_type_name} {mesh_type_name} occult item loaded successfully. Loaded {len(loaded_objects)} objects.")
            else:
                show_popup("No objects found in the occult item file.", icon='ERROR')
                return {'CANCELLED'}

        except Exception as e:
            show_popup(f"Error loading occult item: {str(e)}", icon='ERROR')
            print(f"Full error details: {e}")
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}

        return {'FINISHED'}

    @property
    def occult_type_items(self):
        return [
            ('Fairy', 'Fairy'),
            ('F_Mermaid', 'Female Mermaid'),
            ('M_Merman', 'Male Merman'),
            ('F_Werewolf', 'Female Werewolf'),
            ('M_Werewolf', 'Male Werewolf'),
        ]

    @property
    def mesh_type_items(self):
        """Return mesh type items based on current occult type"""
        if self.occult_type == 'Fairy':
            return [
                ('Big', 'Wings Big'),
                ('Med', 'Wings Med'),
                ('Small', 'Wings Small'),
            ]
        elif self.occult_type == 'F_Mermaid':
            return [
                ('Tail', 'Tail'),
            ]
        elif self.occult_type == 'M_Merman':
            return [
                ('Tail', 'Tail'),
            ]
        elif self.occult_type == 'F_Werewolf':
            return [
                ('Head', 'Head'),
                ('Top', 'Top'),
                ('Bottom', 'Bottom'),
                ('Feet', 'Feet'),
            ]
        elif self.occult_type == 'M_Werewolf':
            return [
                ('Head', 'Head'),
                ('Top', 'Top'),
                ('Bottom', 'Bottom'),
                ('Feet', 'Feet'),
            ]
        return [('NONE', 'None')]


# Register and unregister functions
def register():
    bpy.utils.register_class(TSCT_OT_load_occult)

def unregister():
    bpy.utils.unregister_class(TSCT_OT_load_occult)
