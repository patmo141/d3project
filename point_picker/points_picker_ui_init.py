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
# NONE!

# Module imports
from ..subtrees.addon_common.common import ui


class PointsPicker_UI_Init():

    ###################################################
    # draw init

    def ui_setup(self):
        # UI Box functionality
        # NONE!
        
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
        #ui.button(label='ui.button', title = 'self.tool_action() method linked to button', parent=ui_tools, on_mouseclick=self.tool_action)    
        
        #create a collapsille container to hold a few variables
        container = ui.collapsible('ui.collapse container', parent = self.ui_main)
        
        i1 = ui.labeled_input_text(label='ui.labeled_input_text', 
                              title='float property to BoundFLoat', 
                              value= self.variable_1) 
    
        i2 = ui.labeled_input_text(label='ui.labled_input_text', 
                              title='integer property to BoundInt', 
                              value= self.variable_2)
        
        
        i3 = ui.input_checkbox(
                label='ui.input_checkbox',
                title='True/False property to BoundBool')
    
        container.builder([i1, i2, i3])
        
        

        
    #def set_ui_text(self):
    #    """ sets the viewport text """
    #    self.reset_ui_text()
    #    for i,val in enumerate(['add', 'grab', 'remove']):
    #        self.inst_paragraphs[i].set_markdown(chr(65 + i) + ") " + self.instructions[val])

    #def reset_ui_text(self):
    #    """ clears the viewport text """
    #    for inst_p in self.inst_paragraphs:
    #        inst_p.set_markdown('')

    ###################################################
