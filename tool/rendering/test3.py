import bpy
import os
import mathutils
import numpy as np
import math

# Define your object file path and output directory

object_file_path = '/mnt/chenjh/Idea23D/tool/i23d/TripoSR/output/0/mesh.obj'  # or .glb, etc.
output_directory = '/mnt/chenjh/Idea23D/tool/rendering'

# Scene Setup
def setup_scene():
    bpy.context.scene.render.engine = 'CYCLES'  # Use Cycles engine for rendering
    bpy.context.scene.cycles.samples = 128  # Number of samples per render for quality

# Load Object
def load_object(filepath):
    # Clear existing objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Import the object
    if filepath.endswith('.obj'):
        # bpy.ops.import_scene.obj(filepath=filepath)
        bpy.ops.import_scene.obj(filepath=filepath, vertex_color=True)
    elif filepath.endswith('.glb'):
        bpy.ops.import_scene.gltf(filepath=filepath)
    else:
        print("Unsupported file format")
        return

    obj = bpy.context.selected_objects[0]
    material = bpy.data.materials.new(name="MyMaterial")
    material.diffuse_color = (1, 0, 0, 1)  # Set the material color (red in this example)
    obj.data.materials.append(material)

# Setup Camera
def setup_camera(location, rotation):
    # Create a new camera object
    bpy.ops.object.camera_add(location=location)
    camera = bpy.context.object
    camera.rotation_euler = rotation
    bpy.context.scene.camera = camera

# Setup Lighting
def setup_lighting(type='SUN', location=(0, 0, 10)):
    bpy.ops.object.light_add(type=type, location=location)

# Render Setup
def render_setup(output_path, resolution=(1920, 1080)):
    bpy.context.scene.render.image_settings.file_format = 'PNG'  # Output format
    bpy.context.scene.render.filepath = output_path
    bpy.context.scene.render.resolution_x = resolution[0]
    bpy.context.scene.render.resolution_y = resolution[1]

# Render Scene
def render_scene():
    bpy.ops.render.render(write_still=True)

# Main Function
def main():
    setup_scene()
    load_object(object_file_path)

    camera_locations = [(0, -3, 0), (3, 0, 0)]  # Define camera locations
    camera_rotations = [(math.radians(90), 0, math.radians(90)), (0, math.radians(90), 0)]  # Define camera rotations
    
    setup_lighting()

    for idx, (location, rotation) in enumerate(zip(camera_locations, camera_rotations)):
        setup_camera(location, rotation)
        output_path = os.path.join(output_directory, f'render_{idx}.png')
        render_setup(output_path)
        render_scene()

if __name__ == '__main__':
    main()


# /mnt/chenjh/blender/blender-3.5.0-linux-x64/blender -b -P /mnt/chenjh/Idea23D/tool/rendering/test3.py /mnt/chenjh/Idea23D/tool/i23d/TripoSR/output/0/mesh.obj obj /mnt/chenjh/Idea23D/tool/rendering

