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
    def __init__(self, parent, cursorobj, ax, fig_canvas):
        self.parentframe = parent
        self.cursorobj = cursorobj
        self.solver = solver.solver()
        self.slgen = curvetrackplot.slopetrackplot()
        self.ax = ax
        self.fig_canvas = fig_canvas
    def create_widget(self):
        self.parentframe['borderwidth'] = 1
        self.parentframe['relief'] = 'solid'
        self.title = ttk.Label(self.parentframe, text='Gradient Solver',font=tk.font.Font(weight='bold'))
        self.title.grid(column=0, row=0, sticky=(tk.E,tk.W))
        self.parentframe.columnconfigure(2, weight=1)

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
                             '3. α(free)->β(free), VCLα(fix)')
        self.fitmode_v = tk.StringVar(value=self.fitmode_list[0])
        self.fitmode_cb = ttk.Combobox(self.modeframe,textvariable=self.fitmode_v,height=len(self.fitmode_list),width=28)
        self.fitmode_cb.grid(column=1, row=0, sticky=(tk.E))
        self.fitmode_cb['values'] = self.fitmode_list
        self.fitmode_cb.state(["readonly"])

        self.doit_b = ttk.Button(self.modeframe, text='Do It',command=self.execsolver)
        self.doit_b.grid(column=1, row=1, sticky=(tk.E,tk.W))

        self.mapsyntax_v = tk.BooleanVar(value=True)
        self.mapsyntax_b = ttk.Checkbutton(self.modeframe, text='mapsyntax', variable=self.mapsyntax_v,onvalue=True,offvalue=False)
        self.mapsyntax_b.grid(column=0, row=1, sticky=(tk.E))
            
    def make_cursorlist(self):
        for key in self.cursor_vals:
            #currentval = self.cursor_widgets[key]['var'].get()
            self.cursor_widgets[key]['cb']['values'] = tuple(self.cursorobj.keys())
    def execsolver(self):
        mode = self.fitmode_v.get()
        iid_A = self.cursor_widgets['α']['var'].get()
        iid_B = self.cursor_widgets['β']['var'].get()
        iid_C = self.cursor_widgets['γ']['var'].get()

        lenVC_A = self.params_widgets['VCL α']['var'].get()
        lenVC_B = self.params_widgets['VCL β']['var'].get()
        grad1 = self.params_widgets['Gr. 1']['var'].get()

        cursor_tmp = self.cursorobj[iid_A].values
        pos_tmp = np.array([cursor_tmp['Distance'],cursor_tmp['Height']])
        phi_tmp = cursor_tmp['Angle']
        posA = pos_tmp
        phiA = phi_tmp
        grA = cursor_tmp['Gradient']

        cursor_tmp = self.cursorobj[iid_B].values
        pos_tmp = np.array([cursor_tmp['Distance'],cursor_tmp['Height']])
        phi_tmp = cursor_tmp['Angle']
        posB = pos_tmp
        phiB = phi_tmp
        grB = cursor_tmp['Gradient']

        R = lenVC_A/(phiB - phiA)

        result = self.solver.curvetrack_relocation(posA,phiA,posB,phiB,0,0,'line',R)

        trackpos = self.slgen.generate_single(posA,phiA,phiB,lenVC_A,slen=result[0])
        self.ax.plot(trackpos[:,0], trackpos[:,1])
        self.fig_canvas.draw()

        param_str = self.gen_paramstr_single(mode, result, iid_A, iid_B, posA, posB, lenVC_A, R)
        print()
        print(param_str)
        
        if self.mapsyntax_v.get():
            mapsyntax = self.generate_mapsyntax(result, posA[0], grA, grB, lenVC_A)
            print(mapsyntax)
            
    def generate_mapsyntax(self, result, distA, grA, grB, lenVC_A):
        syntax_str = ''
        syntax_str += '$pt_a = {:f};'.format(distA) + '\n'

        shift = result[0]
        tmp_dist = shift
        syntax_str += '$pt_a {:s}{:f};'.format('+' if tmp_dist>=0 else '',tmp_dist) + '\n'

        syntax_str += 'Gradient.Interpolate({:f});'.format(grA)+'\n'

        tmp_dist = shift + lenVC_A
        syntax_str += '$pt_a {:s}{:f};'.format('+' if tmp_dist>=0 else '',tmp_dist) + '\n'

        syntax_str += 'Gradient.Interpolate({:f});'.format(grB)+'\n'

        return syntax_str
    def gen_paramstr_single(self, fitmode, result, iidA, iidB, posA, posB, lenVC_A, R_A):
        param_str = ''

        #param_str += '\n'
        param_str += '[Gradient fitting]\n'
        param_str += 'Inputs:\n'
        param_str += '   Fitmode:          {:s}\n'.format(fitmode)
        param_str += '   Cursor values:    (Distance, Gradient)\n'
        param_str += '      α ({:s}):      ({:f}, {:f})\n'.format(iidA,posA[0],posA[1])
        param_str += '      β ({:s}):      ({:f}, {:f})\n'.format(iidB,posB[0],posB[1])
        param_str += '   VCL α:            {:f}\n'.format(lenVC_A)
        param_str += '      (RVC α:        {:f})\n'.format(R_A)
        param_str += 'Results:\n'
        #param_str += '   startPt:          ({:f}, {:f})\n'.format(result[1][0][0], result[1][0][1])
        param_str += '   shift from pt. α: {:f}\n'.format(result[0])
        return param_str
        
        
        
        
            
            
            
