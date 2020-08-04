'''
Created on Dec 30, 2019

@author: Patrick
'''
'''
Copyright (C) 2018 CG Cookie
https://github.com/CGCookie/retopoflow
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

import bpy
import bgl
import bmesh

from ..subtrees.addon_common.cookiecutter.cookiecutter import CookieCutter
from ..subtrees.addon_common.common.useractions import ActionHandler

from ..subtrees.addon_common.common.maths import Point2D
from ..subtrees.addon_common.common import ui
from ..subtrees.addon_common.common.drawing import Drawing
from ..subtrees.addon_common.common.blender import tag_redraw_all

from ..subtrees.addon_common.common.boundvar import BoundInt, BoundFloat, BoundBool

#some settings container
options = {}
options["variable_1"] = 5.0
options["variable_3"] = True

#override this pass through to allow anything in 3dview to pass through
def in_region(reg, x, y):
    #first, check outside of area
    if x < reg.x: return False
    if y < reg.y: return False
    if x > reg.x + reg.width: return False
    if y > reg.y + reg.height: return False
    
    return True

class CookieCutter_SculptPassThrough(CookieCutter):
    bl_idname = "view3d.cookiecutter_pass_through_sculpt"
    bl_label = "CookieCutter Sculpt Pass Through"

    default_keymap = {
        'commit': {'RET'},
        'cancel': {'ESC'},
        'action': {'LEFTMOUSE'},
        # 'lasso': {'SHIFT+CTRL+EVT_TWEAK_L'},
        'box': {'B'}
    }

    old_mask_data = []
    first_update = True

    #for this, checkout "polystrips_props.py'
    @property
    def variable_2_gs(self):
        return getattr(self, '_var_cut_count_value', 0)
    @variable_2_gs.setter
    def variable_2_gs(self, v):
        if self.variable_2 == v: return
        self.variable_2 = v
        #if self.variable_2.disabled: return

    def start_pre(self):
        context = bpy.context
        scene = context.scene
        tool_settings = context.tool_settings

        brush_size = 5

        self.sculpt_brush = bpy.data.brushes.new("Pass Through Brush", mode='SCULPT')
        self.sculpt_brush.sculpt_tool = "MASK"

        bpy.ops.object.mode_set(mode='SCULPT')
        
        tool_settings.unified_paint_settings.size = brush_size

        mesh = context.object.data
        bm = bmesh.new()
        bm.from_mesh(mesh)

        if not bm.verts.layers.paint_mask:
            paint_mask = bm.verts.layers.paint_mask.new()
        else:
            paint_mask = bm.verts.layers.paint_mask[0]

        for i in bm.verts:
            self.old_mask_data.append(i[paint_mask])
            i[paint_mask] = 0.0

        bm.to_mesh(mesh)
        bm.clear()
        mesh.update()

    def end_post(self):
        context = bpy.context
        scene = context.scene

        bpy.data.brushes.remove(self.sculpt_brush)
        bpy.ops.object.mode_set(mode='OBJECT')

        mesh = context.object.data
        bm = bmesh.new()
        bm.from_mesh(mesh)

        paint_mask = bm.verts.layers.paint_mask[0]

        for idx, i in enumerate(bm.verts):
            i[paint_mask] = self.old_mask_data[idx]

        bm.to_mesh(mesh)
        bm.clear()
        mesh.update()

    ### Redefine/OVerride of defaults methods from CookieCutter ###
    def start(self):
        self.start_pre()

        opts = {
            'pos': 9,
            'movable': True,
            'bgcolor': (0.2, 0.2, 0.2, 0.8),
            'padding': 0,
            }
        
        
        #some data storage, simple single variables for now
        #later, can use a dictionary and some smarter stuff
        self.variable_1 = BoundFloat('''options['variable_1']''', min_value =0.5, max_value = 15.5)
        self.variable_2 = BoundInt('''self.variable_2_gs''',  min_value = 0, max_value = 10)
        self.variable_3 = BoundBool('''options['variable_3']''')
        
        keymaps = {}
        keymaps['done'] = {'ESC'}
        keymaps['cancel'] = {'ESC'}
        keymaps['finish'] = {'RET'}
        keymaps['box'] = {'B'}

        self.actions = ActionHandler(self.context, keymaps)
        self.setup_ui()

                
        
    def update(self):
        if self.first_update:
            bpy.context.scene.tool_settings.sculpt.brush = self.sculpt_brush
            self.first_update = False

    def end_commit(self):
        pass
    
    def end_cancel(self): 
        pass
    
    def end(self):  #happens after end_commit or end_cancel
        pass
        self.end_post()
    
    ######## End Redefinitions from CookieCutter Class ###
    
    #typically, we would definte these somewhere else
    def do_something(self):
        context = bpy.context

        mesh = context.object.data
        bm = bmesh.new()
        bm.from_mesh(mesh)

        paint_mask = bm.verts.layers.paint_mask[0]

        for i in bm.verts:
            if i[paint_mask] < 0.5:
                bm.verts.remove(i)

        new_mesh = bpy.data.meshes.new("mask")
        obj = bpy.data.objects.new("mask", new_mesh)

        context.collection.objects.link(obj)

        bm.to_mesh(new_mesh)
        bm.clear()
        new_mesh.update()
    
    def setup_ui(self):
        
        #go ahead and open these files
        #addon_common.common.ui
        #addon_common.cookiecutter.cookiecutter_ui
        
        #know that every CookieCutter instance has self.document upon startup
        #most of our ui elements are going to be children of self.document.body
        
        #we generate our UI elements using the methods in ui.py
        
        #we need to read ui_core, particulalry UI_Element
        
        
        
        #collapsible, and framed_dialog
        #first, know
        
        self.ui_main = ui.framed_dialog(label = 'ui.framed_dialog',
                                          resiable = None,
                                          resiable_x = True,
                                          resizable_y=False, 
                                          closeable=False, 
                                          moveable=True, 
                                          hide_on_close=False,
                                          parent=self.document.body)
        
        # tools
        ui_tools = ui.div(id="tools", parent=self.ui_main)
        ui.button(label='Do Something', title = 'self.tool_action() method linked to button', parent=ui_tools, on_mouseclick=self.do_something)    
        
    
    

    
    def should_pass_through(self, context, event):
        
        print(self._hover_ui)
        if self._hover_ui: return False
        
        
        if context.area.type != "VIEW_3D":
            return False

        allowed = ["MOUSEMOVE", "LEFTMOUSE"]

        if event.type not in allowed:
            return False

        #first, check outside of area
        outside = False
        if event.mouse_x < context.area.x: outside = True
        if event.mouse_y < context.area.y: outside = True
        if event.mouse_x > context.area.x + context.area.width: outside = True
        if event.mouse_y > context.area.y + context.area.height: outside = True

        if outside:
            print('outside the 3DView area')
            return False
        
        #make sure we are in the window region, not the header, tools or UI
        for reg in context.area.regions:
            if in_region(reg, event.mouse_x, event.mouse_y) and reg.type != "WINDOW":
                print('in wrong region')
                return False
        
        return True
        
    @CookieCutter.FSM_State('main')
    def modal_main(self):
        Drawing.set_cursor('DEFAULT')

        if self.actions.pressed('action'):
            print('aaaaaaaaaand action \n\n')
            return 'action'

        if self.actions.pressed('lasso'):
            bpy.ops.paint.mask_lasso_gesture('INVOKE_DEFAULT')

        if self.actions.pressed('box'):
            bpy.ops.view3d.select_box('INVOKE_DEFAULT')

        if self.actions.pressed('cancel'):
            print('cancelled')
            self.done(cancel = True)
            return 'cancel'
        
        if self.actions.pressed('commit'):
            print('committed')
            self.done()
            return 'finished'
        
        if self.actions.mousemove:
            return 
        
        
    @CookieCutter.FSM_State('action')
    def modal_grab(self):
        Drawing.set_cursor('CROSSHAIR')

        if self.actions.mousemove:
            print('action mousemove!') 
            return 'action'  #can return nothing and stay in this state?
        
        if self.actions.released('action'):
            #self.lbl.set_label('finish action')
            print('finish action')
            return 'main'

        
        
    #there are no drawing methods for this example
    #this is all buttons and input wundows