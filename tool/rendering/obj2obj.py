import os
import numpy as np
try:
    import cupy as cp
    USE_CUDA = True
except ImportError:
    USE_CUDA = False
from PIL import Image

# 读取OBJ文件
def read_obj(file_path):
    vertices = []
    faces = []
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('v '):
                data = line.split()[1:]
                vertex = [float(data[0]), float(data[1]), float(data[2])]
                color = [float(data[3]), float(data[4]), float(data[5])]
                vertices.append((vertex, color))
            elif line.startswith('f '):
                face = [int(idx.split('/')[0]) for idx in line.split()[1:]]
                faces.append(face)
    return vertices, faces

# 生成UV坐标和法线
def generate_uvs_normals(vertices, faces):
    uvs = []
    normals = []
    for face in faces:
        v1 = vertices[face[0] - 1][0]
        v2 = vertices[face[1] - 1][0]
        v3 = vertices[face[2] - 1][0]
        
        # 计算法线
        normal = calculate_normal(v1, v2, v3)
        normals.extend([normal, normal, normal])
        
        # 计算UV坐标
        uv1, uv2, uv3 = calculate_uvs(v1, v2, v3)
        uvs.extend([uv1, uv2, uv3])
    
    return uvs, normals

# 计算法线
def calculate_normal(v1, v2, v3):
    vec1 = [v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2]]
    vec2 = [v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2]]
    
    normal = [vec1[1] * vec2[2] - vec1[2] * vec2[1],
              vec1[2] * vec2[0] - vec1[0] * vec2[2],
              vec1[0] * vec2[1] - vec1[1] * vec2[0]]
    
    length = (normal[0] ** 2 + normal[1] ** 2 + normal[2] ** 2) ** 0.5
    return [normal[0] / length, normal[1] / length, normal[2] / length]

# 计算UV坐标
def calculate_uvs(v1, v2, v3):
    # 假设UV坐标范围为[0, 1]
    return [(v1[0], v1[2]), (v2[0], v2[2]), (v3[0], v3[2])]

# 生成纹理图像
def generate_texture(vertices, image_path):
    if USE_CUDA:
        vertices = cp.array([v[0] + v[1] for v in vertices])
    else:
        vertices = np.array([v[0] + v[1] for v in vertices])

    width = max(vertices[:, 0]) - min(vertices[:, 0])
    height = max(vertices[:, 2]) - min(vertices[:, 2])
    image = Image.new('RGB', (int(width * 100), int(height * 100)))
    pixels = image.load()

    if USE_CUDA:
        x = (cp.floor((vertices[:, 0] - cp.min(vertices[:, 0])) * 100)).astype(int)
        y = (cp.floor((vertices[:, 2] - cp.min(vertices[:, 2])) * 100)).astype(int)
        colors = (vertices[:, 3:] * 255).astype(int)

        for i in range(len(vertices)):
            pixels[x[i], y[i]] = tuple(colors[i])
    else:
        cnt = 0
        for vertex in vertices:
            cnt += 1
            print(f'{cnt} / {len(vertices)}')
            
            x = int((vertex[0] - min(vertices[:, 0])) * 100)
            y = int((vertex[2] - min(vertices[:, 2])) * 100)
            color = [int(c * 255) for c in vertex[3:]]
            pixels[x, y] = tuple(color)

    image.save(image_path)

# 输出新的OBJ格式
def write_obj(file_path, vertices, faces, uvs, normals, texture_path):
    mtl_path = os.path.splitext(file_path)[0] + '.mtl'
    with open(file_path, 'w') as obj_file, open(mtl_path, 'w') as mtl_file:
        mtl_file.write(f'newmtl material\n')
        mtl_file.write(f'map_Kd {os.path.basename(texture_path)}\n')
        
        obj_file.write(f'mtllib {os.path.basename(mtl_path)}\n')
        obj_file.write(f'usemtl material\n')
        
        for vertex in vertices:
            obj_file.write(f'v {vertex[0][0]} {vertex[0][1]} {vertex[0][2]}\n')
        
        for uv in uvs:
            obj_file.write(f'vt {uv[0]} {uv[1]}\n')
        
        for normal in normals:
            obj_file.write(f'vn {normal[0]} {normal[1]} {normal[2]}\n')
        
        for face in faces:
            face_indices = [str(idx) + '/' + str(idx) + '/' + str(idx) for idx in face]
            obj_file.write(f'f {" ".join(face_indices)}\n')

# 主函数
def convert_obj(input_path, output_path, texture_path):
    vertices, faces = read_obj(input_path)
    print('generate_uvs_normals...')
    uvs, normals = generate_uvs_normals(vertices, faces)
    print('generate_texture..')
    generate_texture(vertices, texture_path)
    print('write_obj...')
    write_obj(output_path, [v[0] for v in vertices], faces, uvs, normals, texture_path)

# 使用示例
input_path = '/mnt/chenjh/Idea23D/input/0/mesh.obj'
output_path = '/mnt/chenjh/Idea23D/input/0/mesh2.obj'
texture_path = '/mnt/chenjh/Idea23D/input/0/texture.png'

convert_obj(input_path, output_path, texture_path)