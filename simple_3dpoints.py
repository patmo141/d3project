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

from .subtrees.addon_common.cookiecutter.cookiecutter import CookieCutter

from .subtrees.addon_common.common.maths import Point2D
from .subtrees.addon_common.common import ui
from .subtrees.addon_common.common.drawing import Drawing

from .subtrees.addon_common.common.boundvar import BoundInt, BoundFloat, BoundBool


#some settings container
options = {}
options["variable_1"] = 5.0
options["variable_3"] = True


class CookieCutter_UITest(CookieCutter):
    bl_idname = "view3d.cookiecutter_ui_test"
    bl_label = "CookieCutter UI Test (Example)"

    default_keymap = {
        'commit': 'RET',
        'cancel': 'ESC',
        'action': 'LEFTMOUSE'
    }

    #for this, checkout "polystrips_props.py'
    @property
    def variable_2_gs(self):
        return getattr(self, '_var_cut_count_value', 0)
    @variable_2_gs.setter
    def variable_2_gs(self, v):
        if self.variable_2 == v: return
        self.variable_2 = v
        #if self.variable_2.disabled: return

    ### Redefine/OVerride of defaults methods from CookieCutter ###
    def start(self):
        opts = {
            'pos': 9,
            'movable': True,
            'bgcolor': (0.2, 0.2, 0.2, 0.8),
            'padding': 0,
            }
        
        
        #some data storage, simple single variables for now
        #later, more coplex dictionaries or container class
        self.variable_1 = BoundFloat('''options['variable_1']''', min_value =0.5, max_value = 15.5)
        self.variable_2 = BoundInt('''self.variable_2_gs''',  min_value = 0, max_value = 10)
        self.variable_3 = BoundBool('''options['variable_3']''')
        
        self.setup_ui()
        
        
        
    def update(self):
        self.ui_action.set_label('Press: %s' % (','.join(self.actions.now_pressed.keys()),))

    def end_commit(self):
        pass
    
    def end_cancel(self): 
        pass
    
    def end(self):  #happens after end_commit or end_cancel
        pass
    
    ######## End Redefinitions from CookieCutter Class ###
    
    #typically, we would definte these somewhere else
    def tool_action(self):
        print('tool action')
        return
    
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
        ui.button(label='ui.button', title = 'self.tool_action() method linked to button', parent=ui_tools, on_mouseclick=self.tool_action)    
        
        #create a collapsille container to hold a few variables
        container = ui.collapsible('ui.collapse container', parent = self.ui_main)
        
        i1 = ui.labeled_input_text(label='Sui.labeled_input_text', 
                              title='float property to BoundFLoat', 
                              value= self.variable_1) 
    
        i2 = ui.labeled_input_text(label='ui.labled_input_text', 
                              title='integer property to BoundInt', 
                              value= self.variable_2)
        
        
        i3 = ui.input_checkbox(
                label='ui.input_checkbox',
                title='True/False property to BoundBool')
    
        container.builder([i1, i2, i3])
    
    
    @CookieCutter.FSM_State('main')
    def modal_main(self):
        Drawing.set_cursor('DEFAULT')

        if self.actions.pressed('action'):
            print('aaaaaaaaaand action \n\n')
            return 'action'

        if self.actions.pressed('cancel'):
            print('cancelled')
            self.done(cancel = True)
            return 'cancel'
        
        if self.actions.pressed('commit'):
            print('committed')
            self.done()
            return 'finished'
        
        
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