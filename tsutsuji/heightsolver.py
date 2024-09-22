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

        self.spacerframe_1 = ttk.Frame(self.parentframe, padding='3 3 3 3')
        self.spacerframe_1.grid(column=1, row=0, sticky=(tk.E,tk.W))

        self.cursorframe = ttk.Frame(self.parentframe, padding='3 3 3 3')
        self.cursorframe.grid(column=2, row=0, sticky=(tk.E))
        
        self.cursor_vals = ('α', 'β', 'γ')
        self.cursor_widgets = {}
        pos=0
        for key in self.cursor_vals:
            self.cursor_widgets[key] = {}
            self.cursor_widgets[key]['label'] = ttk.Label(self.cursorframe, text=key)
            self.cursor_widgets[key]['label'].grid(column=pos*2, row=0, sticky=(tk.E,tk.W))
            self.cursor_widgets[key]['var'] = tk.StringVar()
            self.cursor_widgets[key]['cb'] = ttk.Combobox(self.cursorframe, textvariable=self.cursor_widgets[key]['var'], width=5)
            self.cursor_widgets[key]['cb'].grid(column=pos*2+1, row=0, sticky=(tk.E,tk.W))
            pos+=1
            self.cursor_widgets[key]['cb'].state(["readonly"])
        self.make_cursorlist()

        self.paramsframe = ttk.Frame(self.parentframe, padding='3 3 3 3')
        self.paramsframe.grid(column=0, row=1, sticky=(tk.E,tk.W))

        self.params_vals = ('VCL α', 'VCL β', 'Gr. 1')
        self.params_widgets = {}
        pos=0
        row=0
        for key in self.params_vals:
            self.params_widgets[key] = {}
            self.params_widgets[key]['label'] = ttk.Label(self.paramsframe, text=key)
            self.params_widgets[key]['label'].grid(column=pos, row=row*2, sticky=(tk.E,tk.W))
            self.params_widgets[key]['var'] = tk.DoubleVar()
            self.params_widgets[key]['ent'] = ttk.Entry(self.paramsframe, textvariable=self.params_widgets[key]['var'],width=8)
            self.params_widgets[key]['ent'].grid(column=pos, row=row*2+1, sticky=(tk.E,tk.W))
            pos+=1
            if pos%4 == 0:
                pos = 0
                row+=1

        self.spacerframe_2 = ttk.Frame(self.parentframe, padding='3 3 3 3')
        self.spacerframe_2.grid(column=1, row=1, sticky=(tk.E,tk.W))

        self.modeframe = ttk.Frame(self.parentframe, padding='3 3 3 3')
        self.modeframe.grid(column=2, row=1, sticky=(tk.E))

        self.fitmode_label = ttk.Label(self.modeframe,text='mode')
        self.fitmode_label.grid(column=0, row=0, sticky=(tk.E))
        self.fitmode_list = ('1. α(fix)->β(free)',\
                             '2. α(free)->β(fix)',\
                             '3. α(free)->β(free)')
        self.fitmode_v = tk.StringVar(value=self.fitmode_list[0])
        self.fitmode_cb = ttk.Combobox(self.modeframe,textvariable=self.fitmode_v,height=len(self.fitmode_list),width=28)
        self.fitmode_cb.grid(column=1, row=0, sticky=(tk.E))
        self.fitmode_cb['values'] = self.fitmode_list
        self.fitmode_cb.state(["readonly"])

        self.doit_b = ttk.Button(self.modeframe, text='Do It',command=None)
        self.doit_b.grid(column=1, row=1, sticky=(tk.E,tk.W))

        self.mapsyntax_v = tk.BooleanVar(value=True)
        self.mapsyntax_b = ttk.Checkbutton(self.modeframe, text='mapsyntax', variable=self.mapsyntax_v,onvalue=True,offvalue=False)
        self.mapsyntax_b.grid(column=0, row=1, sticky=(tk.E))
            
    def make_cursorlist(self):
        for key in self.cursor_vals:
            #currentval = self.cursor_widgets[key]['var'].get()
            self.cursor_widgets[key]['cb']['values'] = tuple(self.cursorobj.keys())
        
            
            
