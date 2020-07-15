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

# Module imports
from ..subtrees.cookiecutter.cookiecutter import CookieCutter


#borrowed from edge filet from Zeffi (included with blend)
def draw_3d_points(context, points, size, color = (1,0,0,1)):
    region = context.region
    rv3d = context.space_data.region_3d


    bgl.glEnable(bgl.GL_POINT_SMOOTH)
    bgl.glPointSize(size)
    # bgl.glEnable(bgl.GL_BLEND)
    bgl.glBlendFunc(bgl.GL_SRC_ALPHA, bgl.GL_ONE_MINUS_SRC_ALPHA)

    bgl.glDepthRange(0, 0.9990)     # squeeze depth just a bit
    bgl.glEnable(bgl.GL_BLEND)

    bgl.glDepthFunc(bgl.GL_LEQUAL)
    bgl.glDepthMask(bgl.GL_FALSE)   # do not overwrite depth

    bgl.glBegin(bgl.GL_POINTS)
    # draw red
    bgl.glColor4f(*color)
    for coord in points:
        vector3d = (coord.x, coord.y, coord.z)
        bgl.glVertex3f(*vector3d)
        # vector2d = view3d_utils.location_3d_to_region_2d(region, rv3d, vector3d)
        # bgl.glVertex2f(*vector2d)
    bgl.glEnd()

    bgl.glDepthFunc(bgl.GL_LEQUAL)
    bgl.glDepthRange(0.0, 1.0)
    bgl.glDepthMask(bgl.GL_TRUE)

    bgl.glDisable(bgl.GL_POINT_SMOOTH)
    bgl.glDisable(bgl.GL_POINTS)
    return

class PointsPicker_UI_Draw():

    ###################################################
    # draw functions


    def create_points_batch(self):
        vertices = [(v.location.x, v.location.y, v.location.z) for v in self.b_pts]        #TODO, use D3Point
        self.points_shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        self.points_batch = batch_for_shader(self.points_shader, 'POINTS', {"pos":vertices})
        
        
        
        
    @CookieCutter.Draw("post3d")
    def draw_postview(self):
        
        
        if not self.points_shader: return
        
        bgl.glDepthMask(bgl.GL_TRUE)
        bgl.glPointSize(8)
        bgl.glDepthFunc(bgl.GL_LEQUAL)
        
        self.points_shader.bind()
        self.points_shader.uniform_float("color", (1,1,1,1))
        self.points_batch.draw(self.points_shader)
        
        bgl.glDepthFunc(bgl.GL_LEQUAL)
        bgl.glDepthMask(bgl.GL_TRUE)
        bgl.glDepthRange(0, 1)
        
        #bgl.glDisable(bgl.GL_POINT_SMOOTH)
        #bgl.glDisable(bgl.GL_POINTS)
        bgl.glPointSize(1)
    
    

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
