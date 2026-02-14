import bpy
import os
import sys

# --- DYNAMIC ARGUMENTS ---
# This allows Node.js to pass the OBJ path directly
argv = sys.argv
argv = argv[argv.index("--") + 1:] # get all args after "--"
OBJ_PATH = argv[0] 
OUTPUT_PATH = argv[1]

def clean_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for mesh in bpy.data.meshes: bpy.data.meshes.remove(mesh)

def run_headless_ant_process(input_path, output_path):
    clean_scene()
    
    # Import
    try:
        bpy.ops.wm.obj_import(filepath=input_path)
    except:
        bpy.ops.import_scene.obj(filepath=input_path)

    # ... [Keep your Phase 1 - 4 logic here] ...

    # Export
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    bpy.ops.wm.obj_export(filepath=output_path)
    print(f"ANT: Blender Exported to {output_path}")

if __name__ == "__main__":
    run_headless_ant_process(OBJ_PATH, OUTPUT_PATH)
