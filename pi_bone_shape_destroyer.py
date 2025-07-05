import bpy

class BoneShapeRemover(bpy.types.Operator):
    bl_idname = "object.remove_bone_shapes"
    bl_label = "Remove Bone Shapes"
    bl_description = "Remove objects with bone_shape or bone_bone_shape in their names"
    
    def execute(self, context):
        removed_count = 0
        # Work with object names instead of object references to avoid StructRNA errors
        objects_to_remove = []
        
        # Get all current object names that match our patterns
        for obj_name in list(bpy.data.objects.keys()):
            try:
                if self.is_bone_shape_object(obj_name):
                    objects_to_remove.append(obj_name)
            except:
                # Skip any problematic objects
                continue
        
        # Remove the objects by name
        for obj_name in objects_to_remove:
            try:
                # Check if object still exists in the collection
                if obj_name in bpy.data.objects:
                    obj = bpy.data.objects[obj_name]
                    bpy.data.objects.remove(obj, do_unlink=True)
                    removed_count += 1
                    print(f"Removed bone shape object: {obj_name}")
            except Exception as e:
                print(f"Failed to remove object {obj_name}: {e}")
        
        if removed_count > 0:
            self.report({'INFO'}, f"Removed {removed_count} bone shape objects")
        return {'FINISHED'}
    
    def is_bone_shape_object(self, name):
        """Check if an object name matches bone shape patterns"""
        name_lower = name.lower()
        
        # Check for exact matches or numbered variations
        base_names = ['bone_shape', 'bone_bone_shape']
        
        for base_name in base_names:
            if name_lower == base_name:
                return True
            # Check for numbered variations like .001, .002, etc.
            if name_lower.startswith(base_name + '.'):
                suffix = name_lower[len(base_name + '.'):]
                if suffix.isdigit():
                    return True
        
        return False

# Global variables to prevent excessive checking
_handler_running = False
_last_check_time = 0
_last_object_count = 0

def remove_bone_shapes_handler(dummy):
    """Handler function for automatic removal on various operations"""
    global _handler_running, _last_check_time, _last_object_count
    
    # Prevent recursive calls
    if _handler_running:
        return
    
    import time
    current_time = time.time()
    current_object_count = len(bpy.data.objects)
    
    # Only check if:
    # 1. More than 1 second has passed since last check, AND
    # 2. The number of objects has changed (something was added/removed)
    if (current_time - _last_check_time < 1.0) or (current_object_count == _last_object_count):
        return
    
    _handler_running = True
    _last_check_time = current_time
    _last_object_count = current_object_count
    
    try:
        print("Object count changed, checking for bone shapes...")
        bpy.ops.object.remove_bone_shapes()
    finally:
        _handler_running = False

def remove_bone_shapes_on_load(dummy):
    """Handler function specifically for file load operations"""
    global _handler_running, _last_check_time, _last_object_count
    
    if _handler_running:
        return
        
    _handler_running = True
    
    import time
    _last_check_time = time.time()
    _last_object_count = len(bpy.data.objects)
    
    try:
        print("File loaded, checking for bone shapes...")
        bpy.ops.object.remove_bone_shapes()
    finally:
        _handler_running = False

def register():
    bpy.utils.register_class(BoneShapeRemover)
    
    # Register handlers for different operations
    # File load - separate handler to always run on load
    bpy.app.handlers.load_post.append(remove_bone_shapes_on_load)
    
    # This catches append and link operations with throttling
    bpy.app.handlers.depsgraph_update_post.append(remove_bone_shapes_handler)

def unregister():
    bpy.utils.unregister_class(BoneShapeRemover)
    
    # Remove handlers
    if remove_bone_shapes_on_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(remove_bone_shapes_on_load)
    
    if remove_bone_shapes_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(remove_bone_shapes_handler)

if __name__ == "__main__":
    register()
    # You can also run it manually
    bpy.ops.object.remove_bone_shapes()