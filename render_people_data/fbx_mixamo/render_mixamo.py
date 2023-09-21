import os
import argparse

parser = argparse.ArgumentParser(description='Renders given FBX file by rotating a camera around it.')
parser.add_argument(
    '--save_folder', type=str, default='./tmp',
    help='path for saving rendered image')
parser.add_argument(
    '--dataset_folder', type=str, default='./tmp',
    help='path for downloaded 3D dataset folder')
parser.add_argument(
    '--blender_root', type=str, default='./tmp',
    help='path for Blender')
args = parser.parse_args()

save_folder = args.save_folder
dataset_folder = args.dataset_folder
blender_root = args.blender_root

synset_list = [
    #'mixamo'  # human
    'interviewer_test'
]
scale_list = [
    0.9
]
for synset, fbx_scale in zip(synset_list, scale_list):
    file_list = sorted(os.listdir(os.path.join(dataset_folder, synset)))
    for idx, file in enumerate(file_list):
        render_cmd = '%s -b -P render_all_mixamo_fbx.py -- --output %s %s  --scale %f --views 96 --resolution 1024 >> tmp.out' % (
            blender_root, save_folder, os.path.join(dataset_folder, synset, file, 'model.fbx'), fbx_scale
        )
        os.system(render_cmd)
