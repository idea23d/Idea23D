import bpy
import os
import sys
import argparse
from mathutils import Vector

bpy.context.scene.render.engine = 'CYCLES'  # Or 'BLENDER_EEVEE'

def parse_obj_for_vertex_colors(obj_file_path):
    vertices = []
    colors = []
    faces = []

    with open(obj_file_path, 'r') as file:
        for line in file:
            parts = line.split()
            if line.startswith('v '):  # Vertex with color
                vertex = list(map(float, parts[1:4]))  # Convert vertex position to float
                color = list(map(float, parts[4:7]))  # Convert color to float
                vertices.append(vertex)
                colors.append(color)
            elif line.startswith('f'):  # Face
                face = [int(p.split('/')[0]) for p in parts[1:]]  # Convert face indices to integer
                faces.append(face)

    return vertices, colors, faces

# Example usage - replace 'path_to_your_obj_file.obj' with your actual file path
# vertices, colors, faces = parse_obj_for_vertex_colors('path_to_your_obj_file.obj')


def import_obj_with_vertex_colors(obj_file_path):
    # Attempt to import the mesh
    bpy.ops.import_scene.obj(filepath=obj_file_path, axis_forward='-Z', axis_up='Y')
    
    # Find the last imported object by looking for the object with the highest creation timestamp
    obj = max(bpy.context.scene.objects, key=lambda o: o.select_get(), default=None)
    
    if obj is None:
        print("No object was imported. Check if the file path is correct and the OBJ file is valid.")
        return
    
    bpy.context.view_layer.objects.active = obj  # Set the imported object as active
    obj.select_set(True)  # Ensure it's selected for operations like setting origin

    mesh = obj.data

    # Prepare for vertex color layer
    if not mesh.vertex_colors:
        mesh.vertex_colors.new()

    color_layer = mesh.vertex_colors.active

    # Parse the .obj file to extract vertex colors
    vertex_colors = []
    with open(obj_file_path, 'r') as file:
        for line in file:
            if line.startswith('v '):  # Vertex definition
                parts = line.split()
                # Assuming color immediately follows vertex position
                r, g, b = float(parts[4]), float(parts[5]), float(parts[6])
                vertex_colors.append((r, g, b))

    # Apply the vertex colors to the mesh
    for poly in mesh.polygons:
        for idx, loop_index in enumerate(poly.loop_indices):
            loop_vert_index = mesh.loops[loop_index].vertex_index
            color_layer.data[loop_index].color = vertex_colors[loop_vert_index] + (1.0,)

    # Update mesh to see changes
    mesh.update()

    print(f"Imported '{obj_file_path}' with vertex colors.")



def setup_scene(obj_file):
    # Clear the scene
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()
    # Import the OBJ file with default settings
    import_obj_with_vertex_colors(obj_file)
    bpy.ops.import_scene.obj(filepath=obj_file, axis_forward='-Z', axis_up='Y')

def center_object():
    obj = bpy.context.selected_objects[0]  # Assuming the imported OBJ is the selected object
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
    obj.location = (0, 0, 0)

def setup_camera_and_light():
    # Create a new camera
    bpy.ops.object.camera_add(location=(0, 0, 0))
    camera = bpy.context.object
    bpy.context.scene.camera = camera

    # Create a new light
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
    light = bpy.context.object
    light.data.energy = 3  # Adjust based on your scene

    return camera

def look_at(obj_camera, point):
    direction = point - obj_camera.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    obj_camera.rotation_euler = rot_quat.to_euler()

def set_camera_for_view(camera, view):
    directions = {
        'front': ((0, -10, 3), (0, 0, 0)),
        'back': ((0, 10, 3), (0, 0, 3.14159)),
        'left': ((-10, 0, 3), (0, 0, 1.5708)),
        'right': ((10, 0, 3), (0, 0, -1.5708)),
        'top': ((0, 0, 10), (-1.5708, 0, 0)),
        'bottom': ((0, 0, -10), (1.5708, 0, 3.14159)),
    }
    pos, rot = directions[view]
    camera.location = Vector(pos)
    camera.rotation_euler = Vector(rot)
    look_at(camera, Vector((0, 0, 0)))  # Assuming object is centered at origin

import bpy

def create_mesh_with_vertex_colors(vertices, colors, faces):
    # Create new mesh and object
    mesh = bpy.data.meshes.new("ColoredMesh")
    obj = bpy.data.objects.new("ColoredObject", mesh)

    # Link object to scene
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    # Create mesh from given vertices and faces
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    # Create vertex color layer
    color_layer = mesh.vertex_colors.new()

    for poly in mesh.polygons:  # Iterate over all polygons
        for idx, loop_index in enumerate(poly.loop_indices):
            loop_vert_index = mesh.loops[loop_index].vertex_index
            # Assign vertex color to each loop vertex
            color_layer.data[loop_index].color = colors[loop_vert_index] + (1.0,)  # Adding alpha

    # Update mesh with new data
    mesh.update()

# Assuming vertices, colors, and faces are obtained from the previous parsing step
# create_mesh_with_vertex_colors(vertices, colors, faces)


def create_vertex_color_material(obj):
    mat = bpy.data.materials.new(name="VertexColorMaterial")
    obj.data.materials.append(mat)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    for node in nodes:
        nodes.remove(node)
    
    # Create a Principled BSDF shader node
    shader = nodes.new(type='ShaderNodeBsdfPrincipled')
    shader.location = (0, 0)

    # Create a Vertex Color node
    vertex_color = nodes.new(type='ShaderNodeVertexColor')
    vertex_color.layer_name = "Col"  # Use the name of your vertex color layer
    vertex_color.location = (-400, 0)
    
    # Create an Output node
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (200, 0)
    
    # Link nodes
    links.new(vertex_color.outputs['Color'], shader.inputs['Base Color'])
    links.new(shader.outputs['BSDF'], output.inputs['Surface'])
    
    print("Vertex color material created and assigned.")


def render(output_dir, view_name):
    bpy.context.scene.render.filepath = os.path.join(output_dir, f"{view_name}.png")
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_y = 1080
    bpy.context.scene.render.film_transparent = True
    bpy.ops.render.render(write_still=True)

def main():
    parser = argparse.ArgumentParser(description="Render an OBJ file in Blender.")
    parser.add_argument("obj_file", help="The path to the OBJ file.")
    parser.add_argument("output_dir", help="The directory where the images will be saved.")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])

    setup_scene(args.obj_file)
    obj = bpy.context.selected_objects[0]  # Re-select the imported object
    center_object()
    camera = setup_camera_and_light()
    
    if len(obj.data.vertex_colors) > 0:
        create_vertex_color_material(obj)

    for view in ['front', 'back', 'left', 'right', 'top', 'bottom']:
        set_camera_for_view(camera, view)
        render(args.output_dir, view)

if __name__ == "__main__":
    main()


# /mnt/chenjh/blender/blender-3.5.0-linux-x64/blender --background --python /mnt/chenjh/Idea23D/tool/rendering/blender_rendering.py -- /mnt/chenjh/Idea23D/tool/i23d/TripoSR/output/0/mesh.obj /mnt/chenjh/Idea23D/tool/rendering/output

# /mnt/chenjh/blender/blender-3.5.0-linux-x64/blender --background --python /mnt/chenjh/Idea23D/tool/rendering/blender_rendering.py -- /mnt/chenjh/Avatar123/mesh2depth/data/1100050704346030754.obj /mnt/chenjh/Idea23D/tool/rendering/output

