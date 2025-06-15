"""
Extracts lights FBX scene and converts them to XML format, readable by Mitsuba.
"""
# UNCOMMENT IN BLENDER
# import bpy
import os
import mathutils

def clear_scene():
    """
    Clears the Blender scene to default empty settings.
    """
    bpy.ops.wm.read_factory_settings(use_empty=True)

def import_fbx(path):
    """
    Imports an FBX file into Blender.

    :param str path: Path to the FBX file.

    :raises FileNotFoundError: If the FBX file does not exist.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"FBX file not found: {path}")
    bpy.ops.import_scene.fbx(filepath=path)

def get_lights():
    """
    Retrieves all light objects from the current Blender scene.

    :return list: List of Blender light objects.
    """
    return [obj for obj in bpy.data.objects if obj.type == 'LIGHT']

def blender_to_mitsuba_vec(v):
    """
    Converts a Blender vector to Mitsuba coordinate format.

    :param mathutils.Vector v: Blender 3D vector.

    :return str: Mitsuba-formatted vector as a string.
    """
    return f"{v.x} {v.z} {-v.y}"

def write_mitsuba_xml(xml_path, lights):
    """
    Writes light information into a Mitsuba XML file.

    :param str xml_path: Path to save the XML file.
    :param list lights: List of Blender light objects.

    :raises IOError: If the XML file cannot be written.
    """
    try:
        with open(xml_path, "w") as f:
            f.write('<scene version="3.0.0">\n')
            f.write('  <integrator type="path"/>\n')
            for light in lights:
                loc = blender_to_mitsuba_vec(light.location)
                color = light.data.color
                intensity = light.data.energy
                rgb = f"{color[0] * intensity} {color[1] * intensity} {color[2] * intensity}"
                f.write('  <emitter type="point">\n')
                f.write(f'    <point name="position" x="{loc.split()[0]}" y="{loc.split()[1]}" z="{loc.split()[2]}"/>\n')
                f.write(f'    <rgb name="intensity" value="{rgb}"/>\n')
                f.write('  </emitter>\n')
            f.write('</scene>\n')
    except IOError as e:
        raise IOError(f"Failed to write Mitsuba XML file: {xml_path}") from e

def main():
    """
    Main execution function.
    """
    clear_scene()
    import_fbx(fbx_path)
    lights = get_lights()
    write_mitsuba_xml(mitsuba_xml_path, lights)

if __name__ == "__main__":
    # settings
    fbx_path = r"scene11.fbx"
    mitsuba_xml_path = r"scene11.xml"
    main()
