"""
Constants used throughout the Creator Tools addon.
This module centralizes hardcoded values for better maintainability.
"""

# === MESH OPERATIONS ===

# Default merge distance for removing duplicate vertices
# This value is optimized for The Sims 4 mesh precision
DEFAULT_MERGE_DISTANCE = 0.0001

# === VERTEX COLORS ===

# Vertex colors for The Sims 4 mesh properties
# These colors are used to mark different mesh types

# Skin tight mesh - allows body morphs to affect the mesh
VERTEX_COLOR_SKIN_TIGHT = (0.0, 1.0, 0.0, 1.0)  # Pure green

# Robe morph - special morph for flowing garments
VERTEX_COLOR_ROBE_MORPH = (0.247059, 0.941177, 0.0, 1.0)  # Yellow-green

# Foot mesh - marks shoe/foot geometry
VERTEX_COLOR_FOOT = (1.0, 0.0, 0.0, 1.0)  # Pure red

# Smooth normals - indicates smooth shading
VERTEX_COLOR_SMOOTH_NORMALS = (0.0, 0.0, 1.0, 1.0)  # Pure blue

# Sharp normals - indicates flat/sharp shading
VERTEX_COLOR_SHARP_NORMALS = (0.0, 1.0, 1.0, 1.0)  # Cyan

# === BODY TYPE ENUM ===

# Body type options for The Sims 4 rigs
BODY_TYPE_ITEMS = [
    ('ADULT', "Adult", "Adult body type"),
    ('CHILD', "Child", "Child body type"),
]

# === WEIGHT SMOOTHING ===

# Default parameters for weight smoothing operations
DEFAULT_SMOOTH_FACTOR = 0.5
DEFAULT_SMOOTH_REPEAT = 3

# === FILE NAMING ===

# Prefix for S4Studio mesh objects
S4STUDIO_MESH_PREFIX = "s4studio_mesh"
