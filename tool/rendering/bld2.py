import bpy
import os
from mathutils import Vector

def parse_obj_for_vertex_colors(obj_file_path):
    vertices = []
    colors = []
    faces = []

    with open(obj_file_path, 'r') as file:
        for line in file:
            parts = line.split()
            if line.startswith('v '):
                # Vertex with color information
                vertex = list(map(float, parts[1:4]))
                color = list(map(float, parts[4:7]))
                vertices.append(vertex)
                colors.append(color)
            elif line.startswith('f'):
                # Face information
                face = [int(p.split('/')[0]) - 1 for p in parts[1:]]  # OBJ indices start at 1
                faces.append(face)

    return vertices, colors, faces

def create_mesh_with_vertex_colors(vertices, colors, faces):
    mesh = bpy.data.meshes.new(name="ColoredMesh")
    obj = bpy.data.objects.new("ColoredObject", mesh)

    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    color_layer = mesh.vertex_colors.new(name='Col')

    for poly in mesh.polygons:
        for idx, loop_idx in enumerate(poly.loop_indices):
            loop_vert_idx = mesh.loops[loop_idx].vertex_index
            color_layer.data[loop_idx].color = colors[loop_vert_idx] + (1.0,)  # RGBA

def setup_scene(obj_file):
    vertices, colors, faces = parse_obj_for_vertex_colors(obj_file)
    create_mesh_with_vertex_colors(vertices, colors, faces)

def setup_camera_and_light():
    camera_data = bpy.data.cameras.new(name='Camera')
    camera_object = bpy.data.objects.new('Camera', camera_data)
    bpy.context.scene.collection.objects.link(camera_object)
    bpy.context.scene.camera = camera_object
    camera_object.location = (0, -3, 1)

    light_data = bpy.data.lights.new(name="Light", type='POINT')
    light_object = bpy.data.objects.new(name="Light", object_data=light_data)
    bpy.context.collection.objects.link(light_object)
    light_object.location = (0, 0, 3)
    light_object.data.energy = 1000

def main():
    # Example usage
    obj_file = '/mnt/chenjh/Idea23D/tool/i23d/TripoSR/output/0/mesh.obj'  # Update this path
    output_dir = '/mnt/chenjh/Idea23D/tool/rendering/output'  # Update this path

    setup_scene(obj_file)
    setup_camera_and_light()

    # Setup render settings
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_y = 1080
    bpy.context.scene.render.film_transparent = True

    # Render the scene
    render(output_dir, "render_output")

if __name__ == "__main__":
    main()


# /mnt/chenjh/blender/blender-3.5.0-linux-x64/blender --background --python /mnt/chenjh/Idea23D/tool/rendering/blender_rendering.py -- /mnt/chenjh/Idea23D/tool/i23d/TripoSR/output/0/mesh.obj /mnt/chenjh/Idea23D/tool/rendering/output

# /mnt/chenjh/blender/blender-3.5.0-linux-x64/blender --background --python bld2.py 