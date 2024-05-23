import glob
import json
import multiprocessing
import shutil
import subprocess
import time
from dataclasses import dataclass
from typing import Optional
import os

import boto3
import tyro
import wandb
import math


@dataclass
class Args:
    workers_per_gpu: int
    """number of workers per gpu"""

    input_models_path: str
    """Path to a json file containing a list of 3D object files"""

    upload_to_s3: bool = False
    """Whether to upload the rendered images to S3"""

    log_to_wandb: bool = False
    """Whether to log the progress to wandb"""

    num_gpus: int = -1
    """number of gpus to use. -1 means all available gpus"""

    blender_path: str = '/mnt/chenjh/real2char/zero123/objaverse-rendering/blender-3.5.0-linux-x64'
    """blender 本地目录 eg:/mnt/chenjh/real2char/zero123/objaverse-rendering/blender-3.5.0-linux-x64"""

    view_path_root: str = '/mnt/chenjh/real2char/mesh2img/test0321/views_whole_sphere'
    """渲染后的图保存目录"""
    
    vrm_path: str = '/mnt/chenjh/real2char/mesh2img/test0321/data'
    """输入的vrm的目录"""
    
def worker(
    queue: multiprocessing.JoinableQueue,
    count: multiprocessing.Value,
    gpu: int,
    s3: Optional[boto3.client],
    blender_path: str, 
    view_path_root: str
) -> None:
    while True:
        item = queue.get()
        if item is None:
            break

        view_path = os.path.join(view_path_root, item.split('/')[-1][:-4])
        print('worker view_path=', view_path)
        if os.path.exists(view_path):
            queue.task_done()
            print('========', item, 'rendered', '========')
            continue
        else:
            os.makedirs(view_path, exist_ok = True)

        # Perform some operation on the item
        print(item, gpu)
        command = (
            # f"export DISPLAY=:0.{gpu} &&"
            # f" GOMP_CPU_AFFINITY='0-47' OMP_NUM_THREADS=48 OMP_SCHEDULE=STATIC OMP_PROC_BIND=CLOSE "
            f" CUDA_VISIBLE_DEVICES={gpu} "
            f" {blender_path}/blender -b -P scripts/blender_script.py --"
            f" --object_path {item} --output_dir {view_path_root}"
        )
        print('command=======')
        print(command)
        subprocess.run(command, shell=True)

        with count.get_lock():
            count.value += 1

        queue.task_done()


if __name__ == "__main__":
    args = tyro.cli(Args)

    s3 = boto3.client("s3") if args.upload_to_s3 else None
    queue = multiprocessing.JoinableQueue()
    count = multiprocessing.Value("i", 0)
    blender_path = args.blender_path
    view_path_root = args.view_path_root

    if args.log_to_wandb:
        wandb.init(project="objaverse-rendering", entity="prior-ai2")

    # Start worker processes on each of the GPUs
    for gpu_i in range(args.num_gpus):
        for worker_i in range(args.workers_per_gpu):
            worker_i = gpu_i * args.workers_per_gpu + worker_i
            process = multiprocessing.Process(
                target=worker, args=(queue, count, gpu_i, s3, blender_path, view_path_root)
            )
            process.daemon = True
            process.start()

    # Add items to the queue
    with open(args.input_models_path, "r") as f:
        model_paths = json.load(f)

    model_keys = list(model_paths.keys())

    for item in model_keys:
        path = os.path.join(args.vrm_path, model_paths[item])
        print('queue input path=', path)
        queue.put(path)

    # update the wandb count
    if args.log_to_wandb:
        while True:
            time.sleep(5)
            wandb.log(
                {
                    "count": count.value,
                    "total": len(model_paths),
                    "progress": count.value / len(model_paths),
                }
            )
            if count.value == len(model_paths):
                break

    # Wait for all tasks to be completed
    queue.join()

    # Add sentinels to the queue to stop the worker processes
    for i in range(args.num_gpus * args.workers_per_gpu):
        queue.put(None)
