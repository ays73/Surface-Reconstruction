"""
Unit tests for mitsuba_render.py.
"""
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import pytest
from mitsuba_render_h5 import load_emitters, render_scene, render_scenes_h5

def test_load_emitters_missing_file():
    from pathlib import Path
    with pytest.raises(FileNotFoundError):
        load_emitters(Path("nonexistent_folder/nonexistent_scene.xml"))

def test_check_missing_files():
    out = render_scene("nonexistent_folder/nonexistent_scene.obj", "nonexistent_folder/nonexistent_scene.xml")
    assert out[0] is None and out[1] is None

def test_no_scenes():
    """
    Test if a warning is raised if scenes_dir does not contain any OBJ files
    """
    with pytest.warns(UserWarning):
        render_scenes_h5("images", "../images")
        os.remove("../images/renderings.hdf5")

if __name__ == "__main__":
    pytest.main()