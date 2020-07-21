# Copyright (C) 2018 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# System imports
# NONE!

# Blender imports
import bpy
import blf
import bgl
import gpu
from gpu_extras.batch import batch_for_shader


from mathutils import Vector
from bpy_extras import view3d_utils
from bpy_extras.view3d_utils import location_3d_to_region_2d, region_2d_to_vector_3d

# Module imports
from ..subtrees.addon_common.cookiecutter.cookiecutter import CookieCutter
from ..subtrees.addon_common.common.globals import Globals
from ..subtrees.addon_common.common.blender import tag_redraw_all
from ..subtrees.addon_common.common.maths import Point, Vec, Direction, Normal
from ..subtrees.addon_common.common.maths import Point2D, Vec2D, Direction2D
from ..subtrees.addon_common.common.maths import Color
from ..subtrees.addon_common.common.drawing import (
    CC_DRAW,
    CC_2D_POINTS,
    CC_3D_TRIANGLES
)

class PointsPicker_UI_Draw():

    ###################################################
    # draw functions

    def create_points_batch(self):
        vertices = [(v.location.x, v.location.y, v.location.z) for v in self.b_pts]        #TODO, use D3Point
        self.points_shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        self.points_batch = batch_for_shader(self.points_shader, 'POINTS', {"pos":vertices})

    def draw_default_points(self):
        self.points_shader.bind()
        self.points_shader.uniform_float("color", (1,1,1,1))
        self.points_batch.draw(self.points_shader)
        
    def update_ui(self):
        self.create_points_batch()
        print('updating ui')
        tag_redraw_all('Updated Points')
        
    @CookieCutter.Draw("post3d")
    def draw_postview(self):

        def point_to_point2D(xyz:Point):
            xy = location_3d_to_region_2d(bpy.context.region, bpy.context.space_data.region_3d, xyz)
            if xy is None: return None
            return Point2D(xy)

        def draw(color):
            vertices = [(v.location.x, v.location.y, v.location.z) for v in self.b_pts]        #TODO, use D3Point
            vertices = [point_to_point2D(v) for v in vertices]
            point_color = color

            bgl.glEnable(bgl.GL_BLEND)
            CC_DRAW.stipple(pattern=[4,4])
            CC_DRAW.point_size(10)

            with Globals.drawing.draw(CC_2D_POINTS) as draw:
                draw.color(point_color)
                for v in vertices:
                    draw.vertex(v)
                
        bgl.glDepthMask(bgl.GL_TRUE)
        bgl.glPointSize(8)
        bgl.glDepthFunc(bgl.GL_LEQUAL)

        #default ugly square points

        # if self.points_shader:
        #     self.draw_default_points()

        #sexy round points, no depth masking

        draw(Color((0.5,0.8,0.3,1)))
        
        bgl.glDepthFunc(bgl.GL_LEQUAL)
        bgl.glDepthMask(bgl.GL_TRUE)
        bgl.glDepthRange(0, 1)
    

    @CookieCutter.Draw("post2d")
    def draw_postpixel(self):
        
        
        region = bpy.context.region
        rv3d = bpy.context.space_data.region_3d
        dpi = bpy.context.preferences.system.dpi
        blf.size(0, 20, dpi) #fond_id = 0
        for i,pt in enumerate(self.b_pts):
            if pt.label:
                if self.selected == i:
                    color = (0,1,1,1)
                elif self.hovered[1] == i:
                    color = (0,1,0,1)
                else:
                    color = (1,0,0,1)
                #bgl.glColor4f(*color)
                vector2d = view3d_utils.location_3d_to_region_2d(region, rv3d, pt.location)
                blf.position(0, vector2d[0], vector2d[1] + 5, 0)
                blf.draw(0, pt.label) #font_id = 0
