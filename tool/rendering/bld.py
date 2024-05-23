import bpy
import os

# 文件路径
obj_file_path = '/mnt/chenjh/Idea23D/tool/i23d/TripoSR/output/0/mesh.obj'
output_image_path = '/mnt/chenjh/Idea23D/tool/rendering/output_image.png'

# 清除场景
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# 导入 OBJ 文件
bpy.ops.import_scene.obj(filepath=obj_file_path)

# 获取导入的对象
obj = bpy.context.selected_objects[0]

# 设置渲染引擎为 Cycles，以支持顶点颜色渲染
bpy.context.scene.render.engine = 'CYCLES'

# 创建材质并设置为使用顶点颜色
mat = bpy.data.materials.new(name="VertexColorMaterial")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get('Principled BSDF')
if bsdf is not None:
    mat.node_tree.nodes.remove(bsdf)

vertex_color = mat.node_tree.nodes.new(type='ShaderNodeVertexColor')
vertex_color.layer_name = "Col"  # 顶点颜色层的名称
output = mat.node_tree.nodes.get('Material Output')
mat.node_tree.links.new(vertex_color.outputs['Color'], output.inputs['Surface'])

# 应用材质到对象
if obj.data.materials:
    obj.data.materials[0] = mat
else:
    obj.data.materials.append(mat)

# 设置相机
camera = bpy.data.cameras.new("Camera")
camera_obj = bpy.data.objects.new("Camera", camera)
bpy.context.scene.collection.objects.link(camera_obj)
bpy.context.scene.camera = camera_obj
camera_obj.location = (0, -3, 1)
camera_obj.rotation_euler = (1.1, 0, 0)

# 设置光源
light_data = bpy.data.lights.new(name="light_2.80", type='POINT')
light_object = bpy.data.objects.new(name="light_2.80", object_data=light_data)
bpy.context.collection.objects.link(light_object)
light_object.location = (0, -3, 2)

# 设置渲染属性
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.filepath = output_image_path

# 渲染场景
bpy.ops.render.render(write_still=True)


# /mnt/chenjh/blender/blender-3.5.0-linux-x64/blender --background --python /mnt/chenjh/Idea23D/tool/rendering/bld.py -- /mnt/chenjh/Idea23D/tool/i23d/TripoSR/output/0/mesh.obj /mnt/chenjh/Idea23D/tool/rendering/output
