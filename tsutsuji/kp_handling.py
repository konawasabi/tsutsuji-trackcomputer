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

import os
import sys
import pathlib
import re
import argparse
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as filedialog

from lark import Lark, Transformer, v_args, Visitor

from kobushi import loadmapgrammer as lgr
from kobushi import loadheader as lhe
from kobushi import mapinterpreter

class GUI():
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self.master = tk.Toplevel(self.mainwindow)
        self.master.title('Handling kiloposts')
        self.master.protocol('WM_DELETE_WINDOW', self.closewindow)

        self.create_widgets()
        self.sendtopmost()
    def create_widgets(self):
        self.mainframe = ttk.Frame(self.master, padding='3 3 3 3')
        self.mainframe.columnconfigure(0,weight=1)
        self.mainframe.rowconfigure(0,weight=1)
        self.mainframe.grid(column=0, row=0,sticky=(tk.N, tk.W, tk.E, tk.S))

        # ---

        self.fileframe = ttk.Frame(self.mainframe, padding='3 3 3 3')
        self.fileframe.grid(column=0, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))

        self.input_v = tk.StringVar()
        self.output_v = tk.StringVar()

        self.input_b = ttk.Button(self.fileframe, text='Input', command=self.setinputpath)
        self.output_b = ttk.Button(self.fileframe, text='Output', command=self.setoutputpath)
        self.input_e = ttk.Entry(self.fileframe, textvariable=self.input_v,width=80)
        self.output_e = ttk.Entry(self.fileframe, textvariable=self.output_v,width=80)

        self.input_b.grid(column=0, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.input_e.grid(column=1, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.output_b.grid(column=0, row=1, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.output_e.grid(column=1, row=1, sticky = (tk.N, tk.W, tk.E, tk.S))

        # ---

        self.modeframe = ttk.Labelframe(self.mainframe, padding='3 3 3 3', text='Mode')
        self.modeframe.grid(column=0, row=1, sticky = (tk.N, tk.W,  tk.S))

        self.mode_v = tk.StringVar(value='0')

        self.mode0_rb = ttk.Radiobutton(self.modeframe, text='0. evaluate', value='0', variable=self.mode_v)
        self.mode1_rb = ttk.Radiobutton(self.modeframe, text='1. new expression', value='1', variable=self.mode_v)
        '''
        self.mode2_rb = ttk.Radiobutton(self.modeframe, text='2. offset', value='2', variable=self.mode_v)
        self.mode3_rb = ttk.Radiobutton(self.modeframe, text='3. new variable & offset', value='3', variable=self.mode_v)
        self.mode4_rb = ttk.Radiobutton(self.modeframe, text='4. invert', value='4', variable=self.mode_v)
        '''
        self.mode0_rb.grid(column=0, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.mode1_rb.grid(column=1, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))
        '''
        self.mode2_rb.grid(column=2, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.mode3_rb.grid(column=3, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.mode4_rb.grid(column=4, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))
        '''

        # ---

        self.paramframe = ttk.Frame(self.mainframe, padding='3 3 3 3')
        self.paramframe.grid(column=0, row=2, sticky = (tk.N, tk.W,  tk.S))

        self.decval_v = tk.StringVar()
        self.decval_l = ttk.Label(self.paramframe, text='Initialization')
        self.decval_e = ttk.Entry(self.paramframe, textvariable=self.decval_v,width=80)

        self.newexpr_v = tk.StringVar()
        self.newexpr_l = ttk.Label(self.paramframe, text='New expression')
        self.newexpr_e = ttk.Entry(self.paramframe, textvariable=self.newexpr_v,width=80)
        self.decval_l.grid(column=0, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.decval_e.grid(column=1, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))
        
        self.newexpr_l.grid(column=0, row=1, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.newexpr_e.grid(column=1, row=1, sticky = (tk.N, tk.W, tk.E, tk.S))

        # ---

        self.buttonframe = ttk.Frame(self.mainframe, padding='3 3 3 3')
        self.buttonframe.grid(column=0, row=3, sticky = (tk.N, tk.W,  tk.S))

        self.doit_b = ttk.Button(self.buttonframe, text='Do It')
        self.doit_b.grid(column=0, row=1, sticky = (tk.N, tk.W, tk.E, tk.S))
    def closewindow(self):
        self.master.withdraw()
    def sendtopmost(self, event=None):
        self.master.lift()
        self.master.focus_force()
    def setinputpath(self):
        path = filedialog.askopenfilename(initialdir=self.input_v.get())
        if path != '':
            self.input_v.set(path)
            pathobj = pathlib.Path(path)
            
            self.output_v.set(str(pathobj.parent.joinpath('result')))#.joinpath(pathobj.name)))
    def setoutputpath(self):
        path = filedialog.asksaveasfilename(initialdir=self.output_v.get())
        if path != '':
            self.output_v.set(path)


@v_args(inline=True)
class MapInterpreter(mapinterpreter.ParseMap):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def map_element(self, *argument):
        pass
    def include_file(self, path):
        pass
        
class KilopostHandling():
    def __init__():
        self.mapinterp = MapInterpreter(None, None, prompt=True)
