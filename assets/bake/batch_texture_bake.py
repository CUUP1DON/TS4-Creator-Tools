#!/usr/bin/env python3
"""
Batch texture baking script for tt_bake.blend
Processes queued images for each mesh in the TextureTransfer collection.
"""

import bpy
import json
import os
import sys

def main():
    # Get JSON path from command line arguments
    if len(sys.argv) < 2:
        print("Error: No JSON queue file provided")
        return

    json_path = sys.argv[-1]  # Last argument should be the JSON file

    if not os.path.exists(json_path):
        print(f"Error: JSON file not found: {json_path}")
        return

    # Load queue data
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        queues = data.get('queues', {})
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return

    print(f"Loaded queues for {len(queues)} meshes")

    # Import TextureTransfer collection
    try:
        # Assume the collection is already in the scene or import it
        transfer_collection = bpy.data.collections.get("TextureTransfer")
        if not transfer_collection:
            print("Error: TextureTransfer collection not found")
            return

        # Ensure collection is linked to scene
        if transfer_collection.name not in bpy.context.scene.collection.children:
            bpy.context.scene.collection.children.link(transfer_collection)

    except Exception as e:
        print(f"Error setting up collection: {e}")
        return

    # Process each mesh in queues
    for mesh_name, queue_data in queues.items():
        output_folder = queue_data.get('folder', '')
        images = queue_data.get('images', [])

        if not output_folder or not images:
            print(f"Skipping {mesh_name}: invalid queue data")
            continue

        # Ensure output folder exists
        os.makedirs(output_folder, exist_ok=True)

        # Find mesh object
        mesh_obj = None
        for obj in transfer_collection.objects:
            if obj.name == mesh_name and obj.type == 'MESH':
                mesh_obj = obj
                break

        if not mesh_obj:
            print(f"Mesh {mesh_name} not found in collection")
            continue

        print(f"Processing {mesh_name} with {len(images)} images")

        # Process each image
        for idx, image_path in enumerate(images):
            try:
                # Load image
                if not os.path.exists(image_path):
                    print(f"Image not found: {image_path}")
                    continue

                img = bpy.data.images.load(image_path)

                # Find User_Texture node in material
                mat = mesh_obj.data.materials[0] if mesh_obj.data.materials else None
                if not mat or not mat.use_nodes:
                    print(f"No valid material on {mesh_name}")
                    continue

                user_tex_node = None
                for node in mat.node_tree.nodes:
                    if node.name == "User_Texture" and node.type == 'TEX_IMAGE':
                        user_tex_node = node
                        break

                if not user_tex_node:
                    print(f"User_Texture node not found on {mesh_name}")
                    continue

                # Set image to node
                user_tex_node.image = img

                # Find NEW_Texture node for baking target
                new_tex_node = None
                for node in mat.node_tree.nodes:
                    if node.name == "NEW_Texture" and node.type == 'TEX_IMAGE':
                        new_tex_node = node
                        break

                if not new_tex_node:
                    print(f"NEW_Texture node not found on {mesh_name}")
                    continue

                # Set active image for baking
                mat.node_tree.nodes.active = new_tex_node

                # Bake
                bpy.ops.object.select_all(action='DESELECT')
                mesh_obj.select_set(True)
                bpy.context.view_layer.objects.active = mesh_obj

                # Set bake settings
                bpy.context.scene.render.engine = 'CYCLES'
                bpy.context.scene.cycles.bake_type = 'EMIT'

                # Perform bake
                bpy.ops.object.bake(type='EMIT')

                # Save baked image
                if new_tex_node.image:
                    # Generate filename
                    image_basename = os.path.splitext(os.path.basename(image_path))[0]
                    bake_filename = f"{image_basename}_{idx + 1}.png"
                    bake_path = os.path.join(output_folder, bake_filename)

                    # Save image
                    new_tex_node.image.filepath_raw = bake_path
                    new_tex_node.image.file_format = 'PNG'
                    new_tex_node.image.save()

                    print(f"Saved bake: {bake_path}")

                # Clean up loaded image
                bpy.data.images.remove(img)

            except Exception as e:
                print(f"Error processing {image_path} for {mesh_name}: {e}")
                continue

    print("Batch baking completed!")
    bpy.ops.wm.quit_blender()

if __name__ == "__main__":
    main()