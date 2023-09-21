import argparse
import sys
import os
import math
import re
import bpy
from mathutils import Vector, Matrix
import numpy as np
import json

parser = argparse.ArgumentParser(description='Renders given FBX file by rotating a camera around it.')
parser.add_argument('--views', type=int, default=48, help='number of views to be rendered')
parser.add_argument('fbx', type=str, help='Path to the FBX file to be rendered.')
parser.add_argument('--output_folder', type=str, default='/tmp', help='The path the output will be dumped to.')
parser.add_argument('--scale', type=float, default=1, help='Scaling factor applied to model. Depends on size of mesh.')
parser.add_argument('--format', type=str, default='PNG', help='Format of files generated. Either PNG or OPEN_EXR')
parser.add_argument('--resolution', type=int, default=512, help='Resolution of the images.')
parser.add_argument('--engine', type=str, default='CYCLES', help='Blender internal engine for rendering. E.g. CYCLES, BLENDER_EEVEE, ...')

argv = sys.argv[sys.argv.index("--") + 1:]
args = parser.parse_args(argv)

# Set up rendering
context = bpy.context
scene = bpy.context.scene
render = bpy.context.scene.render

render.engine = args.engine
render.image_settings.color_mode = 'RGBA'  # ('RGB', 'RGBA', ...)
render.image_settings.file_format = args.format  # ('PNG', 'OPEN_EXR', 'JPEG, ...)
render.resolution_x = args.resolution
render.resolution_y = args.resolution
render.resolution_percentage = 100
bpy.context.scene.cycles.filter_width = 0.01
bpy.context.scene.render.film_transparent = True

bpy.context.scene.cycles.device = 'GPU'
bpy.context.scene.cycles.diffuse_bounces = 1
bpy.context.scene.cycles.glossy_bounces = 1
bpy.context.scene.cycles.transparent_max_bounces = 3
bpy.context.scene.cycles.transmission_bounces = 3
bpy.context.scene.cycles.samples = 32
bpy.context.scene.cycles.use_denoising = True

def enable_cuda_devices():
    prefs = bpy.context.preferences
    cprefs = prefs.addons['cycles'].preferences
    cprefs.get_devices()

    for compute_device_type in ('CUDA', 'OPENCL', 'NONE'):
        try:
            cprefs.compute_device_type = compute_device_type
            print("Compute device selected: {0}".format(compute_device_type))
            break
        except TypeError:
            pass

    acceleratedTypes = ['CUDA', 'OPENCL']
    accelerated = any(device.type in acceleratedTypes for device in cprefs.devices)
    print('Accelerated render = {0}'.format(accelerated))

    for device in cprefs.devices:
        device.use = not accelerated or device.type in acceleratedTypes
        print('Device enabled ({type}) = {enabled}'.format(type=device.type, enabled=device.use))

    return accelerated

enable_cuda_devices()
context.active_object.select_set(True)
bpy.ops.object.delete()

# Import FBX file
bpy.ops.import_scene.fbx(filepath=args.fbx)

for this_obj in bpy.data.objects:
    if this_obj.type == "MESH":
        this_obj.select_set(True)
        bpy.context.view_layer.objects.active = this_obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.split_normals()

bpy.ops.object.mode_set(mode='OBJECT')
print(len(bpy.context.selected_objects))
obj = bpy.context.selected_objects[0]
context.view_layer.objects.active = obj

# Move the object to the center
obj.location = (0, 0, 0)

def bounds(obj, local=False):
    local_coords = obj.bound_box[:]
    om = obj.matrix_world

    if not local:
        worldify = lambda p: om @ Vector(p[:])
        coords = [worldify(p).to_tuple() for p in local_coords]
    else:
        coords = [p[:] for p in local_coords]

    rotated = zip(*coords[::-1])

    push_axis = []
    for (axis, _list) in zip('xyz', rotated):
        info = lambda: None
        info.max = max(_list)
        info.min = min(_list)
        info.distance = info.max - info.min
        push_axis.append(info)

    import collections

    originals = dict(zip(['x', 'y', 'z'], push_axis))

    o_details = collections.namedtuple('object_details', 'x y z')
    return o_details(**originals)

def get_3x4_RT_matrix_from_blender(cam):
    location, rotation = cam.matrix_world.decompose()[0:2]
    R_world2bcam = rotation.to_matrix().transposed()
    T_world2bcam = -1*R_world2bcam @ location

    RT = Matrix((
        R_world2bcam[0][:] + (T_world2bcam[0],),
        R_world2bcam[1][:] + (T_world2bcam[1],),
        R_world2bcam[2][:] + (T_world2bcam[2],)
        ))
    return RT

mesh_obj = obj
scale = args.scale
factor = max(mesh_obj.dimensions[0], mesh_obj.dimensions[1], mesh_obj.dimensions[2]) / scale
print('Size of object:')
print(mesh_obj.dimensions)
print(factor)
object_details = bounds(mesh_obj)
print(
    object_details.x.min, object_details.x.max,
    object_details.y.min, object_details.y.max,
    object_details.z.min, object_details.z.max,
)
print(bounds(mesh_obj))
mesh_obj.scale[0] /= factor
mesh_obj.scale[1] /= factor
mesh_obj.scale[2] /= factor
bpy.ops.object.transform_apply(scale=True)

bpy.ops.object.light_add(type='AREA')
light2 = bpy.data.lights['Area']

light2.energy = 10000
bpy.data.objects['Area'].location[2] = 2
bpy.data.objects['Area'].scale[0] = 100
bpy.data.objects['Area'].scale[1] = 100
bpy.data.objects['Area'].scale[2] = 100

# Place camera
cam = scene.objects['Camera']
bbox_center = obj.matrix_world @ ((Vector(obj.bound_box[0]) + Vector(obj.bound_box[6])) / 2)
cam.location = bbox_center + Vector((0, -5.0, 0))
cam.data.lens = 80
cam.data.sensor_width = 32

cam_constraint = cam.constraints.new(type='TRACK_TO')
cam_constraint.track_axis = 'TRACK_NEGATIVE_Z'
cam_constraint.up_axis = 'UP_Y'

cam_empty = bpy.data.objects.new("Empty", None)
cam_empty.location = bbox_center
cam.parent = cam_empty

scene.collection.objects.link(cam_empty)
context.view_layer.objects.active = cam_empty
cam_constraint.target = cam_empty

# ... (continued with the rest of your original code)

stepsize = 360.0 / args.views
rotation_mode = 'XYZ'

model_identifier = os.path.split(os.path.split(args.fbx)[0])[1]
synset_idx = args.fbx.split('/')[-3]

img_folder = os.path.join(os.path.abspath(args.output_folder), 'img', synset_idx, model_identifier)
camera_folder = os.path.join(os.path.abspath(args.output_folder), 'camera', synset_idx, model_identifier)

os.makedirs(img_folder, exist_ok=True)
os.makedirs(camera_folder, exist_ok=True)

rotation_angle_list = np.random.rand(args.views)
elevation_angle_list = np.random.rand(args.views)
rotation_angle_list = rotation_angle_list * 360
elevation_angle_list = (elevation_angle_list - 0.5) * 100
np.save(os.path.join(camera_folder, 'rotation'), rotation_angle_list)
np.save(os.path.join(camera_folder, 'elevation'), elevation_angle_list)

# Creation of the transform.json
to_export = {
    'camera_angle_x': bpy.data.cameras[0].angle_x,
    "aabb": [[-scale/2,-scale/2,-scale/2],
             [scale/2,scale/2,scale/2]]
}
frames = []

for i in range(0, args.views):
    cam_empty.rotation_euler[2] = math.radians(rotation_angle_list[i])
    cam_empty.rotation_euler[0] = math.radians(elevation_angle_list[i])

    print("Rotation {}, {}".format((stepsize * i), math.radians(stepsize * i)))
    render_file_path = os.path.join(img_folder, '%03d.png' % i)
    scene.render.filepath = render_file_path
    bpy.ops.render.render(write_still=True)
    # Might not need it, but just in case cam is not updated correctly
    bpy.context.view_layer.update()

    rt = get_3x4_RT_matrix_from_blender(cam)
    pos, rt, scale = cam.matrix_world.decompose()

    rt = rt.to_matrix()
    matrix = []
    for ii in range(3):
        a = []
        for jj in range(3):
            a.append(rt[ii][jj])
        a.append(pos[ii])
        matrix.append(a)
    matrix.append([0, 0, 0, 1])
    print(matrix)

    to_add = {
        "file_path": f'{str(i).zfill(3)}.png',
        "transform_matrix": matrix
    }
    frames.append(to_add)

to_export['frames'] = frames
with open(f'{img_folder}/transforms.json', 'w') as f:
    json.dump(to_export, f, indent=4)
