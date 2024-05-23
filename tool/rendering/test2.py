import bpy
from mathutils import Vector


def setup_scene(obj_file_path, output_image_path):
    # 删除所有对象，确保场景为空
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # 导入OBJ文件
    bpy.ops.import_scene.obj(filepath=obj_file_path)

    # 获取刚导入的对象
    imported_obj = bpy.context.selected_objects[0]

    # 设置顶点颜色材质
    setup_vertex_color_material(imported_obj)

    # 添加灯光和摄像机
    setup_light_and_camera(imported_obj)

    # 设置渲染参数并渲染图像
    render_image(output_image_path)

def setup_vertex_color_material(obj):
    # 创建一个材料并启用节点
    mat = bpy.data.materials.new(name="VertexColorMaterial")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    vertex_color = mat.node_tree.nodes.new('ShaderNodeVertexColor')
    vertex_color.layer_name = 'Col'  # 顶点颜色层的名称
    mat.node_tree.links.new(vertex_color.outputs['Color'], bsdf.inputs['Base Color'])

    # 将材料应用到对象
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
        
def setup_light_and_camera(obj):
    # 确定对象的中心和大小
    center = obj.location
    size = max(obj.dimensions)

    # 添加点光源
    bpy.ops.object.light_add(type='POINT', location=(center.x, center.y, center.z + size * 2))

    # 添加摄像机，并将其定位于对象正前方
    camera_location = center + obj.matrix_world.to_quaternion() @ Vector((0, -size * 3, 0))
    bpy.ops.object.camera_add(location=camera_location)
    camera = bpy.context.object
    camera.data.type = 'PERSP'
    camera.rotation_euler = (1.5708, 0, 0)
    camera.data.lens = 50

    # 摄像机朝向对象
    look_at(camera, center)


def look_at(obj, target):
    """使对象朝向目标点"""
    direction = target - obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    obj.rotation_euler = rot_quat.to_euler()

def render_image(output_image_path):
    # 设置渲染分辨率和输出路径
    bpy.context.scene.render.resolution_x = 1080
    bpy.context.scene.render.resolution_y = 1080
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = output_image_path

    # 设置摄像机
    bpy.context.scene.camera = bpy.context.object

    # 渲染
    bpy.ops.render.render(write_still=True)

# 定义输入和输出路径
# 导入OBJ文件
obj_file_path = '/mnt/chenjh/Idea23D/tool/i23d/TripoSR/output/0/mesh.obj'
# obj_file_path = '/mnt/chenjh/Avatar123/mesh2depth/data/1100050704346030754.obj'
output_image_path = '/mnt/chenjh/Idea23D/tool/rendering/image.png'

# 设置场景并渲染
setup_scene(obj_file_path, output_image_path)
