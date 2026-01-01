# TS4 Creator Tools - Changelog

## Recent Updates

### v1.9 - Major Improvements and Bug Fixes

#### 🐛 Bug Fixes
- **Fixed "Create Bake Duplicate" naming issue**: Objects now duplicate with clean names like `s4studio_mesh_1_bake` instead of `s4studio_mesh_1.001_bake`
- **Fixed batch baking queue progression**: The system now properly processes the next mesh in queue when the previous one finishes baking
- **Removed property not found errors**: Eliminated terminal errors when moving mouse over UI by removing unused preference properties

#### 🔧 Code Organization
- **Moved preferences to separate module**: Created `user_preferences.py` to organize all addon preferences and UI classes
- **Cleaned up main `__init__.py`**: Removed 300+ lines of preference code for better maintainability

#### 🎨 Material Setup Improvements
- **Simplified shader setup**: Replaced Principled BSDF with Diffuse BSDF for cleaner baking materials
- **Updated node naming**: All nodes now have clear, readable names without underscores:
  - "Image Queue Texture" (connected image node)
  - "New Bake" (disconnected baking target)
  - "Diffuse" (shader node)
  - "Output" (material output)
- **Node layout optimization**:
  - All nodes collapsed by default for clean appearance
  - Tight positioning with New Bake above Image Queue Texture
  - Compact layout with minimal spacing

#### ⚙️ Preference Cleanup
- **Removed unused properties**: Eliminated `bake_type`, `bake_use_direct`, and `bake_use_indirect` properties
- **Streamlined bake settings**: Simplified to essential options (device, samples, margin, image dimensions, color)
- **Hardcoded optimal bake settings**: DIFFUSE bake type with color-only pass for consistent results

#### 🔄 Batch Baking Enhancements
- **Improved queue management**: Added `_advance_to_next_queue()` helper for robust queue progression
- **UI synchronization**: Active queue index now updates to show current processing mesh
- **Better error handling**: Added safety checks to prevent crashes with invalid queue data
- **State management**: Proper `is_baking` flag prevents concurrent processing

## Technical Details

### Files Modified
- `__init__.py` - Main addon file, cleaned up and reorganized
- `pi_bakes.py` - Baking functionality, fixed queue progression and material setup
- `user_preferences.py` - New file containing all preference classes and UI

### Key Functions Updated
- `TSCT_OT_DuplicateToTextureTransfer.execute()` - Fixed object naming
- `TSCT_OT_StartBatchTextureBake._start_next_image()` - Improved queue progression
- `TSCT_OT_SetupMaterials.execute()` - Complete material node restructure
- `TSCT_OT_StartBatchTextureBake._process_single_image()` - Updated node name references

### Material Node Structure
```
New Bake             (-300, -25)  [collapsed]
        ↓
Image Queue Texture  (-300, 25)   [collapsed]
        ↓
Diffuse              (0, 0)       [collapsed]
        ↓
Output               (300, 0)     [collapsed]
```

## Installation
1. Copy the addon folder to your Blender addons directory
2. Enable "TS4 Creator Tools" in Blender preferences
3. Access tools from the TS4CT tab in the 3D View sidebar

## Usage
- Use "Create Bake Duplicate" to prepare meshes for batch baking
- Setup UV maps and materials for texture transfer workflow
- Add images to mesh queues and start batch baking
- Monitor progress in the baking panel

## Compatibility
- Blender 4.0+
- Windows 10+
- Cycles render engine required for baking features</content>
</xai:function_call">## Summary of All Changes Made

I've created a comprehensive README.md file documenting all the changes made to the TS4 Creator Tools addon. Here's a summary of what was accomplished:

### 🐛 **Bug Fixes**
- **Fixed "Create Bake Duplicate" naming**: Objects now get clean names like `s4studio_mesh_1_bake` instead of `s4studio_mesh_1.001_bake`
- **Fixed batch baking queue progression**: System now properly advances to next mesh when previous finishes
- **Eliminated property errors**: Removed terminal errors when hovering over UI

### 🔧 **Code Organization** 
- **Created `user_preferences.py`**: Moved all preference classes and UI to separate module
- **Cleaned up `__init__.py`**: Removed 300+ lines of preference code for better maintainability

### 🎨 **Material Setup Overhaul**
- **Simplified shader**: Replaced Principled BSDF with Diffuse BSDF
- **Updated node naming**: Clear names without underscores ("Image Queue Texture", "New Bake", "Diffuse", "Output")
- **Node layout**: All nodes collapsed, tight positioning with New Bake above Image Queue Texture

### ⚙️ **Preference Cleanup**
- **Removed unused properties**: Eliminated `bake_type`, `bake_use_direct`, `bake_use_indirect`
- **Streamlined settings**: Focus on essential bake options
- **Hardcoded optimal settings**: DIFFUSE bake type with color-only pass

### 🔄 **Batch Baking Improvements**
- **Enhanced queue management**: Added helper methods for robust progression
- **UI synchronization**: Active queue index updates to show current mesh
- **Better error handling**: Safety checks prevent crashes
- **State management**: Proper flags prevent concurrent processing

The README provides a complete changelog, technical details, and usage instructions for the updated addon.