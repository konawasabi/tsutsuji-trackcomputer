#
#    Copyright 2024 konawasabi
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#


'''
'''

import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import ttk
import tkinter.colorchooser as colorchooser
import re
import itertools

from kobushi import trackcoordinate

from . import drawcursor
from . import math
from . import solver
from . import curvetrackplot

class heightSolverUI():
    def __init__(self, parent, cursorobj):
        self.parentframe = parent
        self.cursorobj = cursorobj
    def create_widget(self):
        self.parentframe['borderwidth'] = 1
        self.parentframe['relief'] = 'solid'
        self.title = ttk.Label(self.parentframe, text='Gradient Solver',font=tk.font.Font(weight='bold'))
        self.title.grid(column=0, row=0, sticky=(tk.E,tk.W))

        self.cursorframe = ttk.Frame(self.parentframe, padding='3 3 3 3')
        self.cursorframe.grid(column=0, row=1, sticky=(tk.E,tk.W))
        
        self.cursor_vals = ('α', 'β', 'γ')
        self.cursor_widgets = {}
        pos=0
        for key in self.cursor_vals:
            self.cursor_widgets[key] = {}
            self.cursor_widgets[key]['label'] = ttk.Label(self.cursorframe, text=key)
            self.cursor_widgets[key]['label'].grid(column=pos*2, row=0, sticky=(tk.E,tk.W))
            self.cursor_widgets[key]['var'] = tk.StringVar()
            self.cursor_widgets[key]['cb'] = ttk.Combobox(self.cursorframe, textvariable=self.cursor_widgets[key]['var'], width=4)
            self.cursor_widgets[key]['cb'].grid(column=pos*2+1, row=0, sticky=(tk.E,tk.W))
            pos+=1
        self.make_cursorlist()
        
    def make_cursorlist(self):
        for key in self.cursor_vals:
            #currentval = self.cursor_widgets[key]['var'].get()
            self.cursor_widgets[key]['cb']['values'] = tuple(self.cursorobj.keys())
        
            
            
