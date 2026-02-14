import bpy
import json
import sys
import os

# Get Model ID from command line arguments
argv = sys.argv
argv = argv[argv.index("--") + 1:] 
model_id = argv[0]

# Paths
base_path = f"output/CleanedFiles/{model_id}"
obj_path = f"{base_path}/{model_id}.obj"
json_path = f"{base_path}/selection.json"
output_dir = f"{base_path}/Limbs"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def run_separation():
    # 1. Clear scene and import the cleaned OBJ
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.obj_import(filepath=obj_path)
    main_obj = bpy.context.selected_objects[0]
    
    # 2. Load the Selection JSON from Three.js
    with open(json_path, 'r') as f:
        selection_map = json.load(f) # Format: {"Head": [0, 5, 22...], "Arm_L": [10, 11...]}

    # 3. Process each limb
    for limb_name, vert_indices in selection_map.items():
        # Re-select the main object
        bpy.context.view_layer.objects.active = main_obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        
        # Select vertices by index
        bpy.ops.object.mode_set(mode='OBJECT')
        for idx in vert_indices:
            main_obj.data.vertices[idx].select = True
            
        # Separate selected vertices into a new object
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.separate(type='SELECTED')
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Rename the new object (it will be the one currently selected)
        new_part = bpy.context.selected_objects[0]
        new_part.name = limb_name
        
        # Export the specific limb
        limb_file = f"{output_dir}/{limb_name}.obj"
        bpy.ops.wm.obj_export(filepath=limb_file, export_selected_objects=True)
        
        # To avoid confusion, delete the limb object from scene before next loop
        bpy.ops.object.delete()

run_separation()
