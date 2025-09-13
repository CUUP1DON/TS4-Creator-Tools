> [!IMPORTANT]
> This addon was made using the help of claude.ai.

## TS4 Creator Tools v1.7 (8.24.2025)

_Asset Importer:_
- Load Base Body: A directory of default bodies you can load. Includes: head, top, bottom, full body, and feet.
- Load CAS items: A directory of EA CAS items you can load. Includes dresses, skirts, pants, and shirts.

_Anim Importer:_
- Load Rig: Loads base rigs (female and male rigs still have pp).
- Link Rig: Will link a rig to your current mesh. Can Link multiple at once.
- Load Animation: Will import and load animations to rig.
- Clear Animation: Will remove action from currently selected rig and clear all pose transforms.

_REF:_
- Rename Mesh: REF: Renames the mesh you've selected as REF. Addon will use this mesh to do weight and data transfer.
- Subdivide REF Mesh: Subdivides the reference mesh for smoother weight and uv_1 transfer. Limit 10.
- Delete REF Mesh: Deletes the reference mesh.

_Mesh:_
- Rename Mesh S4S: Renames the mesh you've selected to s4studio_mesh_1. Addon will use this as your main mesh.
- Merge By Distance: Remove doubles, merges vertices.
- Set Cut Number: Sets the cut number for the currently selected mesh(es). Requires Sims 4 Studio's addon.
- Tris To Quads: Turns triangulated faces to quads.
- Triangulate Faces: Triangulates faces of a mesh.

_UVs:_
- UV Checker: Checks to make sure your UV maps are present and named. Will rename UV maps to uv_0 and uv_1. Will also add them if they do not exist.
- Data Transfer: Transfers uv_1 data from reference mesh to s4studio_mesh_1.

_Weights:_
- Weight Transfer: Will transfer weights from the reference mesh to s4studio_mesh_1.
- Smooth Weights: Will smooth weights by 4 iterations on the currently selected mesh. Smooths out rough transfers. Use sparingly.
- Limit Weights: Will limit weights by 4 (default). Stops run away weights.

_Transparency Fix:_
- Mark Strip Boundary: In edit mode, it will mark the boundary used to determine what edge to split the mesh at.
- Clear Strip Boundary: Will clear the boundary you marked.
- Fix Transparency: Will triangulate the mesh, split the mesh into strip defined by the boundaries you marked then join them back together and merge the vertices.

_LOD Creation:_
- Generate LOD Levels: Generates LODs of the s4studio_mesh_1 using the decimation modifier. Merge by distance before use. Adds them into their own collection. LOD1: 75% decimation, LOD2: 50% decimation, LOD3: 25% decimation.
- Connect LOD Vertices: Will connect your mesh to EA's body LODs. Make sure vertices are close.
- Wireframe Mode: For when you're trying to connect mesh seams. It's easier to see the vertices and turn on snap tool.

_Vertex Paints:_ 
- Skin Tight: Does what it says :3
- Robe Morph: Does what it says :3
- Hairline: Does what it says :3
- Hair Acc: Does what it says :3
- Black: Disables slider use on meshes it's applied to.
- White: For lamp glows.

_Bakes:_ 
- Create Bake Collection: Does what it says. Makes a collection to put the items you want to use to bake your shadow maps into a collection for import into blend files used for texture map bakes.
- Open Shadow Map Bake: Creates a copy of a blend file you can use to bake shadow maps for your mesh.

## TS4CT: Custom Importer

_Setup:_
- Setup Folders: Creates asset folders in your determined path.

_Asset Folder:_
- Open Assets Folder: Does what it says :3

_CAS:_
- Load CAS Part: Loads the CAS parts you add to the assets folder.

_Body:_
- Load Body: Loads the bodies you add to the assets folder.

_Rig:_
- Load Rig: Loads the rigs you add to the assets folder.
- Link Rig: Will link a rig to your current mesh. Can Link multiple at once.

_Animations:_
- Load Animation: 
- Clear Animation: Will remove action from currently selected rig and clear all pose transforms.

_Settings:_
- Folder Path Settings: Takes you to preferences to changes the asset folder location.
