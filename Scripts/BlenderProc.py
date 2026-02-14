import bpy
import os
import sys

# --- DYNAMIC ARGUMENTS ---
# Getting arguments passed after the "--" flag
try:
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] 
    OBJ_PATH = argv[0] 
    OUTPUT_PATH = argv[1]
except (ValueError, IndexError):
    print("ANT ERROR: Arguments missing. Usage: blender -b -P script.py -- <input_obj> <output_obj>")
    sys.exit(1)

def clean_scene():
    """Removes all existing mesh objects and orphaned data."""
    if bpy.context.object and bpy.context.view_layer.objects.active:
        if bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Purge orphaned data
    for mesh in bpy.data.meshes: bpy.data.meshes.remove(mesh)
    for mat in bpy.data.materials: bpy.data.materials.remove(mat)

def run_headless_ant_process(input_path, output_path, min_face_count=20):
    # 1. Validation
    if not os.path.exists(input_path):
        print(f"ANT ERROR: File not found at {input_path}")
        return

    # 2. Fresh Start
    clean_scene()

    # 3. Import (Supports Blender 4.0+ and older)
    print(f"ANT: Importing {input_path}...")
    try:
        bpy.ops.wm.obj_import(filepath=input_path)
    except AttributeError:
        bpy.ops.import_scene.obj(filepath=input_path)

    # 4. Identify and Center
    imported_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
    
    if not imported_objects:
        print("ANT ERROR: No mesh found in imported file.")
        return

    # Join parts & Set Origin to Geometry
    bpy.context.view_layer.objects.active = imported_objects[0]
    for obj in imported_objects:
        obj.select_set(True)
    
    bpy.ops.object.join()
    
    # --- CENTER ORIGIN ---
    bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='MEDIAN')
    
    target_obj = bpy.context.active_object
    # Set the internal name to the ID (filename without extension)
    target_obj.name = os.path.splitext(os.path.basename(output_path))[0]

    # --- PHASE 1: REPAIR ---
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.001)
    bpy.ops.mesh.tris_convert_to_quads()
    bpy.ops.object.mode_set(mode='OBJECT')

    # --- PHASE 3: SEPARATE & JUNK REMOVAL ---
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.separate(type='LOOSE')
    bpy.ops.object.mode_set(mode='OBJECT')

    keepers = []
    for piece in bpy.context.selected_objects:
        if piece.type == 'MESH':
            if len(piece.data.polygons) >= min_face_count:
                keepers.append(piece)
            else:
                bpy.data.objects.remove(piece, do_unlink=True)

    # --- PHASE 4: FINAL WELD ---
    if keepers:
        for k in keepers: k.select_set(True)
        bpy.context.view_layer.objects.active = keepers[0]
        bpy.ops.object.join()
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=0.001)
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # 5. Export
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        print(f"ANT: Process Complete. Exporting to {output_path}")
        
        try:
            bpy.ops.wm.obj_export(filepath=output_path)
        except AttributeError:
            bpy.ops.export_scene.obj(filepath=output_path)
    else:
        print("ANT ERROR: Mesh too small or empty.")

# --- EXECUTION ---
if __name__ == "__main__":
    run_headless_ant_process(OBJ_PATH, OUTPUT_PATH)
