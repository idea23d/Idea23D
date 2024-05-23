CUDA_VISIBLE_DEVICES=5 \
python scripts/distributed.py \
	--num_gpus 8 \
	--workers_per_gpu 8  \
	--view_path_root /mnt/chenjh/Real2Character/dataset/data_views_whole_sphere \
	--blender_path /mnt/chenjh/real2char/zero123/objaverse-rendering/blender-3.5.0-linux-x64 \
	--input_models_path /mnt/chenjh/Real2Character/dataset/obj-path-14k-2.json \
	--vrm_path /mnt/chenjh/real2char/dataset/data/data

	# --num_gpus 8 \
	# --workers_per_gpu 8  \
	# --view_path_root /mnt/chenjh/real2char/dataset/data/data_views_whole_sphere \ 这是要保存渲染图片的输出目录
	# --blender_path /mnt/chenjh/real2char/zero123/objaverse-rendering/blender-3.5.0-linux-x64 \ blender路径
	# --input_models_path /mnt/chenjh/real2char/dataset/data/obj-path-7k.json \ 这个是有效obj path
	# --vrm_path /mnt/chenjh/real2char/dataset/data/data 这个是vrm存放路径

# python scripts/distributed.py \
# 	--num_gpus 8 \
# 	--workers_per_gpu 2 \
# 	--input_models_path /mnt/chenjh/real2char/mesh2img/test0321/object-paths-obj.json

# /mnt/chenjh/blender/blender-3.5.0-linux-x64/blender --background --python /mnt/chenjh/Idea23D/tool/rendering/blender_rendering.py -- /mnt/chenjh/Idea23D/tool/i23d/TripoSR/output/0/mesh.obj /mnt/chenjh/Idea23D/tool/rendering

# /mnt/chenjh/blender/blender-3.5.0-linux-x64/blender -b -P /mnt/chenjh/Idea23D/tool/rendering/blender_rendering.py -- --object_path "/mnt/chenjh/Idea23D/tool/i23d/TripoSR/output/0/mesh.obj" --output_dir "/mnt/chenjh/Idea23D/tool/rendering" --engine CYCLES --scale 0.8 --num_images 12 --camera_dist 1.2

# /mnt/chenjh/blender/blender-3.5.0-linux-x64/blender -b -P /mnt/chenjh/Idea23D/tool/rendering/blender_rendering.py /mnt/chenjh/Idea23D/tool/i23d/TripoSR/output/0/mesh.obj obj /mnt/chenjh/Idea23D/tool/rendering


#  CUDA_VISIBLE_DEVICES=0 /mnt/chenjh/blender/blender-3.5.0-linux-x64/blender -b -P scripts/blender_script.py -- --object_path /mnt/chenjh/Idea23D/tool/i23d/TripoSR/output/0/mesh.obj --output_dir /mnt/chenjh/Idea23D/tool/rendering