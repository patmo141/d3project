bl_info = {
    "name": "CC Examples",
    "author":  "Jonathan Denning, Patrick Moore, Christopher Gearhart, ",
    "version": (1, 0),
    "blender": (2, 81, 0),
    "location": "",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "https://github.com/cgcookie/addon_common/issues",
    "category": "View 3D",
}


import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector


from .simple_ui import CookieCutter_UITest
from .point_picker import CookieCutterPoints
from .selective_pass_through import CookieCutter_PassTrhoughTest

def register():
    bpy.utils.register_class(CookieCutter_UITest)
    bpy.utils.register_class(CookieCutterPoints)
    bpy.utils.register_class(CookieCutter_PassTrhoughTest)

def unregister():
    bpy.utils.unregister_class(CookieCutter_UITest)
    bpy.utils.unregister_class(CookieCutterPoints)
    bpy.utils.register_class(CookieCutter_PassTrhoughTest)

if __name__ == "__main__":
    register()
