"""
Offers functionalities to render scenes given by OBJ objects and XML lights
"""

import mitsuba as mi
import xml.etree.ElementTree as ET
import math
import numpy as np
import h5py
import argparse
import os
import warnings
from pathlib import Path
from glob import glob
from tqdm import tqdm

def load_emitters(xml_path):
    """
    Loads emitters from a Mitsuba XML scene.

    :param str xml_path: Path to the XML file.
    :return list[dict]: List of emitter dictionaries.
    :raises FileNotFoundError: If the XML file does not exist.
    """
    if not os.path.exists(xml_path):
        raise FileNotFoundError(f"Emitter XML file not found: {xml_path}")

    emitters = []
    tree = ET.parse(xml_path)
    root = tree.getroot()
    for emitter in root.findall("emitter"):
        if emitter.get("type") == "point":
            pos = emitter.find("point")
            intensity = emitter.find("rgb")
            emitters.append({
                "position": tuple(map(float, [pos.get("x"), pos.get("y"), pos.get("z")])),
                "intensity": list(map(float, intensity.get("value").split()))
            })
    return emitters

def render_scene(obj_path, xml_light_path):
    """
    Renders a scene given by OBJ and XML lights.

    :param str obj_path: path to the OBJ file.
    :param str xml_light_path: path to the XML light file.
    :return ndarray: rendered image as np.array
    """

    if not os.path.exists(obj_path) or not os.path.exists(xml_light_path):
        return None, None

    emitters = load_emitters(xml_light_path)

    obj_dict = {
        'type': 'obj',
        'filename': obj_path,
        'face_normals': False,
        'bsdf': {
            'type': 'diffuse',
            'reflectance': {'type': 'rgb', 'value': [0.8, 0.8, 0.8]}
        }
    }
    temp_scene = mi.load_dict({'type': 'scene', 'object': obj_dict})
    mesh = temp_scene.shapes()[0]
    bbox = mesh.bbox()

    center = (bbox.min + bbox.max) * 0.5
    extent = bbox.max - bbox.min
    scale = max(extent.x, extent.y, extent.z) / 10.0
    angle_rad = math.radians(5)
    radius = max(extent.x, extent.z) * 2.0

    # camera position can be changed
    camera_pos = [
        center.x + radius * math.cos(angle_rad),
        center.y + extent.y * 1.5,
        center.z + radius * math.sin(angle_rad)
    ]
    camera_target = [center.x, center.y, center.z]
    camera_up = [0, 3, 0]

    scaled_emitters = []
    for e in emitters:
        pos = [e["position"][j] * scale + camera_target[j] for j in range(3)]
        scaled_emitters.append({
            "type": "point",
            "position": pos,
            "intensity": [v * 500000 for v in e["intensity"]]
        })

    scene_dict = {
        'type': 'scene',
        'integrator': {'type': 'path'},
        'sensor': {
            'type': 'perspective',
            'fov': 45,
            'to_world': mi.Transform4f().look_at(
                mi.Point3f(*camera_pos),
                mi.Point3f(*camera_target),
                mi.Vector3f(*camera_up),
            ),
            'sampler': {'type': 'independent', 'sample_count': 256},
            'film': {
                'type': 'hdrfilm',
                'width': 800,
                'height': 600,
                'rfilter': {'type': 'box'}
            }
        },
        'geometry': obj_dict,
    }

    for i, emitter in enumerate(scaled_emitters):
        scene_dict[f"emitter_{i}"] = {
            "type": emitter["type"],
            "position": emitter["position"],
            "intensity": {"type": "rgb", "value": emitter["intensity"]}
        }

    scene = mi.load_dict(scene_dict)
    image = mi.render(scene)

    return np.array(image)

def render_scenes_h5(scene_dir, out_path):
    """
    Renders all scenes, given by OBJ and XML files in a directory and saves them as PNGs and HDF5.

    :param str scene_dir: Path to the scene directory.
    :param str out_path: Path to the output directory.
    """
    scene_images = {}
    pattern = os.path.join(scene_dir,"*.obj") # change pattern if you want to
    obj_files = glob(pattern)
    obj_files = list(obj_files)
    if len(list(obj_files)) == 0:
        warnings.warn(f"No OBJ files found in {scene_dir}")

    for obj_file in tqdm(obj_files, desc="Rendering scenes"):
        scene_name = Path(obj_file).stem
        xml_file = os.path.join(scene_dir,f"{scene_name}.xml")
        if not os.path.exists(xml_file):
            raise ValueError(f"XML lights file {xml_file} does not exist")

        img = render_scene(obj_file, xml_file)
        bmp = mi.Bitmap(img).convert(pixel_format=mi.Bitmap.PixelFormat.RGB, component_format=mi.Struct.Type.UInt8)
        bmp.write(os.path.join(out_path,f"{scene_name}.png"))
        if img is not None:
            scene_images[scene_name] = img

    hdf_path = os.path.join(out_path, "renderings.hdf5")
    with h5py.File(hdf_path, "w") as h5f:
        for name, img in scene_images.items():
            h5f.create_dataset(name, data=img, compression="gzip")

def main():
    """
    Main function that parses inputs and runs render_scenes_h5()
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene_dir", help="Directory where scenes are saved",
                        default= "demo_scene")
    parser.add_argument("--out_path", help="Directory where renderings should be saved",
                        default=os.getcwd())

    args = parser.parse_args()
    scene_dir = args.scene_dir
    out_path = args.out_path

    mi.set_variant('scalar_rgb')

    render_scenes_h5(scene_dir, out_path)


if __name__ == "__main__":
    main()
