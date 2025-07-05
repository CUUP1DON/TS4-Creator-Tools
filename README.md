> [!IMPORTANT]
> This addon was made using the help of claude.ai.

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
- Set Cut Number: Sets the cut number for the currently selected mesh(s). Requires Sims 4 Studio's addon.
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
Disclaimer: This addon was made using the help of claude.ai

## TS4 Creator Tools v1.6 (7.5.2025)
- Made it so your mesh doesn't have to be named S4Studio_Mesh_1 to change vertex colors
- Added the BONE SHAPE DESTROYER - goodbye unnecessary empty object
- Added the ability to load rigs and body meshes
- Added black and white vertex colors
- Made it so link rig will use the existing armature modifier instead of adding additional ones
- Made it so link rig will use any armature with the word ‘rig’ in it
- Made it so link rig will ask you WHAT rig you want to link if there are multiple present in the scene
- Made it so the REF mesh won’t be deleted after transferring weights
- Added delete REF mesh button
- Added button to add or change Cut #. Can change multiple meshes cut # if they’re selected at the same time
- Added button to make LODs EZ. Use merge by distance so they don’t split apart at the seams
- Added button to enable wireframe and the snap tool to make connecting seams of meshes easier
- Made it so check uv button doesn't make dupes of the uv_1
- Made some of the boxes prettier
- Made it so the limit for subdividing the REF mesh is 10
- Fixed issue where it would sometimes duplicate weights (i hope)
- see you in another year lol

## TS4 Creator Tools v1.5 (5.14.2024)
- Support for Blender 3.6. Might not work in 4.0+ but you can try.
- Added Rename Mesh: It quickly renames your meshes to what the addon needs to work. I.e. s4studio_mesh_1 or REF quickly.
- Added UV Checker: It adds and renames maps if needed. I.e. if your mesh has no uv_1, it will add it so you can do a data transfer without worrying about it.
- Added Subdivide: Gives more polys to the REF mesh and helps make weights and uv_1 smoother.
- Added Data Transfer: Transfers the uv_1 without you having to do it yourself.
- Added Remove Doubles: Removes vertices that are duplicate and/or very close together. Helpful for keeping meshes together at their seams.
- Added Tris to Quads & Triangulate Faces: Changes the face types of your mesh. Helpful for more precise UV Map editing and making the mesh more game ready. Helps prevent small run-away weights in game.
- Added Weight Transfer: Transfer weights from REF mesh to s4studio_mesh_1 without you having to do it yourself.
- Added Link Rig: Link rig to mesh in a single click.
- Added Smooth Weights: Will smooth the weights of the mesh. I recommend using remove doubles if your mesh is edge split, it will keep the mesh together at the seams. Automatically turns off mirroring when used.
- Added Limit Weights: TS4 only accepts 4 weights per vertex in a mesh, more than that gets limited. Helps prevent run-away weights in game.
- Added Vertex Paints: Assign a vertex color to your mesh in a single click. 
