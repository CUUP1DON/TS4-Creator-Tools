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
_handlers_registered = False
_timer_registered = False

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
    # 1. More than 0.3 seconds has passed since last check, AND
    # 2. The number of objects has changed (something was added/removed)
    if (current_time - _last_check_time < 0.3) or (current_object_count == _last_object_count):
        return
    
    _handler_running = True
    _last_check_time = current_time
    _last_object_count = current_object_count
    
    try:
        print("Object count changed, checking for bone shapes...")
        bpy.ops.object.remove_bone_shapes()
    finally:
        _handler_running = False

def timer_check_bone_shapes():
    """Timer function that periodically checks for bone shapes"""
    global _handler_running
    
    if _handler_running:
        return 0.5  # Check again in 0.5 seconds
    
    # Quick check if there are any bone shapes to remove
    bone_shapes_found = False
    for obj_name in bpy.data.objects.keys():
        if obj_name.lower().startswith(('bone_shape', 'bone_bone_shape')):
            bone_shapes_found = True
            break
    
    if bone_shapes_found:
        try:
            bpy.ops.object.remove_bone_shapes()
        except:
            pass
    
    return 2.0  # Check again in 2 seconds

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

def ensure_handlers_registered():
    """Ensure handlers are registered, even in existing files"""
    global _handlers_registered, _timer_registered
    
    if _handlers_registered:
        return
    
    # Clean up any existing handlers first to avoid duplicates
    unregister_handlers()
    
    # Register multiple handlers to catch different events
    bpy.app.handlers.load_post.append(remove_bone_shapes_on_load)
    bpy.app.handlers.depsgraph_update_post.append(remove_bone_shapes_handler)
    
    # Also register for scene update events
    if hasattr(bpy.app.handlers, 'scene_update_post'):
        bpy.app.handlers.scene_update_post.append(remove_bone_shapes_handler)
    
    # Add a timer that periodically checks for bone shapes
    if not _timer_registered:
        bpy.app.timers.register(timer_check_bone_shapes, first_interval=1.0)
        _timer_registered = True
    
    _handlers_registered = True
    print("Bone shape removal handlers registered")

def unregister_handlers():
    """Remove all handlers"""
    global _handlers_registered, _timer_registered
    
    # Remove handlers if they exist
    if remove_bone_shapes_on_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(remove_bone_shapes_on_load)
    
    if remove_bone_shapes_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(remove_bone_shapes_handler)
    
    if hasattr(bpy.app.handlers, 'scene_update_post') and remove_bone_shapes_handler in bpy.app.handlers.scene_update_post:
        bpy.app.handlers.scene_update_post.remove(remove_bone_shapes_handler)
    
    # Remove timer
    if _timer_registered and bpy.app.timers.is_registered(timer_check_bone_shapes):
        bpy.app.timers.unregister(timer_check_bone_shapes)
        _timer_registered = False
    
    _handlers_registered = False

def register():
    bpy.utils.register_class(BoneShapeRemover)
    
    # Always ensure handlers are registered when this module is registered
    ensure_handlers_registered()
    
    # Also run a check immediately in case we're in an existing file with bone shapes
    try:
        bpy.ops.object.remove_bone_shapes()
    except:
        pass  # Ignore errors if context isn't ready

def unregister():
    bpy.utils.unregister_class(BoneShapeRemover)
    unregister_handlers()

if __name__ == "__main__":
    register()
    # You can also run it manually
    bpy.ops.object.remove_bone_shapes()