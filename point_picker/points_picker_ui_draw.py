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
from mathutils import Vector, Matrix, Color, kdtree
import gpu
from gpu_extras.batch import batch_for_shader


from mathutils import Vector
from bpy_extras import view3d_utils
from bpy_extras.view3d_utils import location_3d_to_region_2d, region_2d_to_vector_3d

# Module imports
from ..subtrees.addon_common.cookiecutter.cookiecutter import CookieCutter
from .points_picker_render import D3PointsRender
from ..subtrees.addon_common.common.globals import Globals
from ..subtrees.addon_common.common.blender import tag_redraw_all
from ..subtrees.addon_common.common.maths import Point, Vec, Direction, Normal
from ..subtrees.addon_common.common.maths import Point2D, Vec2D, Direction2D
from ..subtrees.addon_common.common.maths import matrix_normal, Direction
from ..subtrees.addon_common.common.maths import Color
from ..subtrees.addon_common.common.drawing import (
    CC_DRAW,
    CC_2D_POINTS,
    CC_3D_TRIANGLES
)

from ..subtrees.addon_common.common.maths import Ray, XForm, BBox, Plane

class PointsPicker_UI_Draw():
    ###################################################
    # draw functions

    def update_ui(self):
        self.d3_points_render._gather_data()
        print('updating ui')
        tag_redraw_all('Updated Points')
        
    @CookieCutter.Draw("post3d")
    def draw_postview(self):
        buf_matrix_target = XForm(Matrix.Identity(4)).mx_p # self.rftarget_draw.buf_matrix_model
        buf_matrix_target_inv = XForm(Matrix.Identity(4)).imx_p # self.rftarget_draw.buf_matrix_inverse
        buf_matrix_view = self.actions.r3d.view_matrix # XForm.to_bglMatrix(self.actions.r3d.view_matrix)
        buf_matrix_view_invtrans = matrix_normal(self.actions.r3d.view_matrix) # XForm.to_bglMatrix(matrix_normal(self.actions.r3d.view_matrix))
        buf_matrix_proj = self.actions.r3d.window_matrix # XForm.to_bglMatrix(self.actions.r3d.window_matrix)
        view_forward = self.actions.r3d.view_rotation @ Vector((0,0,-1))

        bgl.glEnable(bgl.GL_MULTISAMPLE)
        bgl.glEnable(bgl.GL_LINE_SMOOTH)
        bgl.glHint(bgl.GL_LINE_SMOOTH_HINT, bgl.GL_NICEST)
        bgl.glEnable(bgl.GL_BLEND)
        # bgl.glEnable(bgl.GL_POINT_SMOOTH)
        if True:  #why?
            alpha_above,alpha_below = 1.0 , 0.1
            cull_backfaces = False
            alpha_backface = 0.01
            self.d3_points_render.draw(
                view_forward, 1.0,
                buf_matrix_target, buf_matrix_target_inv,
                buf_matrix_view, buf_matrix_view_invtrans, buf_matrix_proj,
                alpha_above, alpha_below, cull_backfaces, alpha_backface
            )

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
                else:
                    color = (1,0,0,1)
                #bgl.glColor4f(*color)
                vector2d = view3d_utils.location_3d_to_region_2d(region, rv3d, pt.location)
                if vector2d:
                    blf.position(0, vector2d[0] + 10, vector2d[1] - 5, 0)
                    blf.draw(0, pt.label) #font_id = 0
