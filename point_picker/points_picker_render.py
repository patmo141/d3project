
'''
Copyright (C) 2019 CG Cookie
http://cgcookie.com
hello@cgcookie.com

Created by Jonathan Denning, Jonathan Williamson

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import sys
import math
import copy
import json
import time
import random



import bpy
import bgl
import bmesh
from bmesh.types import BMesh, BMVert, BMEdge, BMFace
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

from mathutils import Matrix, Vector
from mathutils.geometry import normal as compute_normal, intersect_point_tri
from ..subtrees.addon_common.common.globals import Globals
from ..subtrees.addon_common.common.debug import dprint, Debugger
from ..subtrees.addon_common.common.profiler import profiler
from ..subtrees.addon_common.common.maths import Point, Direction, Normal, Frame
from ..subtrees.addon_common.common.maths import Point2D, Vec2D, Direction2D
from ..subtrees.addon_common.common.maths import Ray, XForm, BBox, Plane
from ..subtrees.addon_common.common.ui import Drawing
from ..subtrees.addon_common.common.blender import tag_redraw_all
from ..subtrees.addon_common.common.utils import min_index
from ..subtrees.addon_common.common.hasher import hash_object, hash_bmesh
from ..subtrees.addon_common.common.decorators import stats_wrapper
from ..subtrees.addon_common.common import bmesh_render as bmegl
from .d3_point_render import BufferedRender_Batch

from ..subtrees.addon_common.common.colors import colorname_to_color



 # visualization settings
#'target vert size':         4.0,
#'target edge size':         2.0,
#'target alpha':             1.0,
#'target hidden alpha':      0.1,
#'target alpha backface':    0.2,
#'target cull backfaces':    False,

color_mesh = colorname_to_color['indigo']
color_select = colorname_to_color['darkorange']
edge_size = 2.0
vert_size = 20.0
normal_offset_multiplier = 1.0
constrain_offset = True

opts = {
            'point color':                 (*color_mesh[:3],   1.00),
            'point color selected':        (*color_select[:3], 1.00),
            'point color highlight':       (1.0, 1.0, 0.1, 1.0),
            'point size':                  vert_size,
            'point size highlight':        10.0,
            'point offset':                0.000015,
            'point dotoffset':             1.0,

            'focus mult':                  1.0,
            'normal offset':               0.001 * normal_offset_multiplier,    # pushes vertices out along normal
            'constrain offset':            constrain_offset,
        }

class D3PointsRender():
    '''
    CurveNetworkRender handles rendering of the SplineNetwork.
    '''

    #what are all the opsts?
    
    def __init__(self, d3_points, opts):
        
        self.buf_matrix_model = XForm(Matrix.Identity(4)).to_bglMatrix_Model()
        self.buf_matrix_inverse = XForm(Matrix.Identity(4)).to_bglMatrix_Inverse()
        self.buf_matrix_normal = XForm(Matrix.Identity(4)).to_bglMatrix_Normal()
        self.buffered_renders = []
        self.drawing = Globals.drawing
        self.time = 0
        self.d3_points = d3_points
        #self.replace_rfmesh(rfmesh)
        self.replace_opts(opts)

    def __del__(self):
        if hasattr(self, 'buf_matrix_model'):
            del self.buf_matrix_model
        if hasattr(self, 'buf_matrix_inverse'):
            del self.buf_matrix_inverse
        if hasattr(self, 'buf_matrix_normal'):
            del self.buf_matrix_normal
        if hasattr(self, 'buffered_renders'):
            del self.buffered_renders

    #@profiler.function
    def replace_opts(self, opts):
        self.opts = opts
        self.opts['dpi mult'] = self.drawing.get_dpi_mult()
        #self.rfmesh_version = None

    #@profiler.function
    def replace_rfmesh(self, rfmesh):
        self.rfmesh = rfmesh
        self.bmesh = rfmesh.bme
        #self.rfmesh_version = None

    #@profiler.function
    def add_buffered_render(self, bgl_type, data):
        batch = BufferedRender_Batch(bgl_type)
        batch.buffer(data['vco'], data['vno'], data['sel'], data['hov'])
        self.buffered_renders.append(batch)
        # buffered_render = BGLBufferedRender(bgl_type)
        # buffered_render.buffer(data['vco'], data['vno'], data['sel'], data['idx'])
        # self.buffered_renders.append(buffered_render)

    #@profiler.function
    def _gather_data(self):
        
        #print('gathering data')
        self.buffered_renders = []  #TODO, smart update only the buffers that need it

        def sel(v):
            if self.d3_points.selected != -1:
                if self.d3_points.b_pts[self.d3_points.selected] == v:
                    print(self.d3_points.selected)
                    return 1.0
            return 0.0

        def hov(v):
            if self.d3_points.hovered[0]:
                if self.d3_points.b_pts[self.d3_points.hovered[1]] == v:
                    return 1.0
            return 0.0

        def gather():
            vert_count = 100000
            '''
            IMPORTANT NOTE: DO NOT USE PROFILER INSIDE THIS FUNCTION IF LOADING ASYNCHRONOUSLY!
            '''
            try:
                time_start = time.time()

                # NOTE: duplicating data rather than using indexing, otherwise
                # selection will bleed
                #pr = profiler.start('gathering', enabled=not self.async_load)
                if True:  #why if True?
                    verts = self.d3_points.b_pts
                    l = len(verts)
                    for i0 in range(0, l, vert_count):
                        i1 = min(l, i0 + vert_count)
                        vert_data = {
                            'vco': [tuple((v.location.x, v.location.y, v.location.z)) for v in verts[i0:i1]],
                            'vno': [tuple((v.location.x, v.location.y, v.location.z)) for v in verts[i0:i1]],
                            'sel': [sel(v) for v in verts[i0:i1]],
                            'hov': [hov(v) for v in verts[i0:i1]],
                            'idx': None,  # list(range(len(self.bmesh.verts))),
                        }
                        
                        self.add_buffered_render(bgl.GL_POINTS, vert_data)

                time_end = time.time()
                # print('RFMeshRender: Gather time: %0.2f' % (time_end - time_start))

            except Exception as e:
                print('EXCEPTION WHILE GATHERING: ' + str(e))
                raise e

        self._is_loading = True
        self._is_loaded = False

        #pr = profiler.start('Gathering data for RFMesh (%ssync)' % ('a' if self.async_load else ''))
        gather()
        
    def clean(self):  #used to only reload if mesh has changed,
        return
    
    def draw(
        self,
        view_forward, unit_scaling_factor,
        buf_matrix_target, buf_matrix_target_inv,
        buf_matrix_view, buf_matrix_view_invtrans,
        buf_matrix_proj,
        alpha_above, alpha_below,
        cull_backfaces, alpha_backface,
    ):
        self.clean()
        if not self.buffered_renders:
            print("no renders")
            return

        try:
            bgl.glDepthMask(bgl.GL_FALSE)       # do not overwrite the depth buffer

            opts = dict(self.opts)

            opts['matrix model'] = self.d3_points.xform.mx_p
            opts['matrix normal'] = self.d3_points.xform.mx_n
            opts['matrix target'] = buf_matrix_target
            opts['matrix target inverse'] = buf_matrix_target_inv
            opts['matrix view'] = buf_matrix_view
            opts['matrix view normal'] = buf_matrix_view_invtrans
            opts['matrix projection'] = buf_matrix_proj
            opts['forward direction'] = view_forward
            opts['unit scaling factor'] = unit_scaling_factor

            bmegl.glSetDefaultOptions()

            opts['cull backfaces'] = cull_backfaces
            opts['alpha backface'] = alpha_backface
            opts['dpi mult'] = self.drawing.get_dpi_mult()
            mirror_axes = [] #self.spline_network.mirror_mod.xyz if self.spline_network.mirror_mod else []
            for axis in mirror_axes: opts['mirror %s' % axis] = True

            #pr = profiler.start('geometry above')
            if True:
                bgl.glDepthFunc(bgl.GL_LEQUAL)
                opts['point hidden']        = 1 - alpha_above
                opts['point mirror hidden'] = 1 - alpha_above
                for buffered_render in self.buffered_renders:
                    buffered_render.draw(opts, self.time)

            if not opts.get('no below', False):
                # draw geometry hidden behind
                #pr = profiler.start('geometry below')
                if True:
                    bgl.glDepthFunc(bgl.GL_GREATER)
                    opts['point hidden']        = 1 - alpha_below
                    opts['point mirror hidden'] = 1 - alpha_below
                    for buffered_render in self.buffered_renders:
                        buffered_render.draw(opts, self.time)
                #pr.done()

            bgl.glDepthFunc(bgl.GL_LEQUAL)
            bgl.glDepthMask(bgl.GL_TRUE)
            bgl.glDepthRange(0, 1)
        except:
            #print('Exception Exception')
            Debugger.print_exception()
            pass

        self.time += 1