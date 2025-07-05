> [!IMPORTANT]
> This addon was made using the help of claude.ai.

## How to Install
_Blender 3.6:_
1. Open Blender.
2. Go to Edit.
3. Go to Prefrences.
4. Go to Add-ons.
5. Click install & find the .zip file.
6. If the addon doesn't pop up on it's own, go to search bar and type in TS4 Creator Tools.
7. Click the check mark box to enable it.
   
_Blender 4.x+_
1. Drag and drop into window.
2. Install addon.

## TS4 Creator Tools v1.6
_Asset Importer:_
- Load Base Body: A directory of default bodies you can load. All EA meshes: top, bottom, full body and feet.
- Load Rig: Loads base rigs (fem and male rigs may have pp, my b).

_Prerequisites:_
- Rename Mesh S4S: Renames the mesh you've selected to s4studio_mesh_1. Addon will use this as your main mesh.
- Rename Mesh: REF: Renames the mesh you've selected as REF. Addon will use this mesh to do weight and data transfer.

_Mesh:_
- Merge By Distance: Remove doubles, merges vertices.
- Subdivide REF Mesh: Subdivides the reference mesh for smoother weight and uv_1 transfer. Limit 10.
- Delete REF Mesh: Deleted the reference mesh.
- Set Cut Number: Sets the cut number for the currently selected mesh(s). _Requires Sims 4 Studio's addon._
- Tris To Quads: Turns triangulated faces to quads.
- Triangulate Faces: Triangulates faces of a mesh.

_UVs:_
- UV Checker: Checks to make sure your UV maps are present and named. Will rename UV maps to uv_0 and uv_1. Will also add them if they do not exist.
- Data Transfer: Transfers uv_1 data from reference mesh to s4studio_mesh_1.

_Weights:_
- Link Rig: Will link a rig to your current mesh.
- Weight Transfer: Will transfer weights from the reference mesh to s4studio_mesh_1.
- Smooth Weights: Will smooth weights by 4 iterations on the currently selected mesh. Smooths out rough transfers. Use sparingly.
- Limit Weights: Will limit weights by 4 (default). Stops run away weights.

_LOD Creation:_
- Generate LOD Levels: Generates LODs of the s4studio_mesh_1 using the decimation modifier. Merge by distance before use. Adds them into their own collections. LOD1: 75% decimation, LOD2: 50% decimation, LOD3: 25% decimation.
- Wireframe Mode: For when you're trying to connect mesh seams. It's easier to see the vertices. Turns on the snap tool to make it easier.

_Vertex Paints:_
- Skin Tight: Does what it says :3
- Robe Morph: Does what it says :3
- Hairline: Does what it says :3
- Hair Acc: Does what it says :3
- Black: Disables slider use on mesh it's applied to.
- White: For lamp glows.
