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

import re

import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as filedialog

class GUI():
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self.master = tk.Toplevel(self.mainwindow)
        self.master.title('Mediantrack generator')
        self.master.protocol('WM_DELETE_WINDOW', self.closewindow)

        self.trackcontrol = self.mainwindow.trackcontrol

        self.create_widgets()
        self.make_trackkeylist()
        self.sendtopmost()
    def create_widgets(self):
        self.mainframe = ttk.Frame(self.master, padding='3 3 3 3')
        self.mainframe.columnconfigure(0,weight=1)
        self.mainframe.rowconfigure(0,weight=1)
        self.mainframe.grid(column=0, row=0,sticky=(tk.N, tk.W, tk.E, tk.S))

        # ---

        self.fileframe = ttk.Frame(self.mainframe, padding='3 3 3 3')
        self.fileframe.grid(column=0, row=1, sticky = (tk.N, tk.W, tk.E, tk.S))

        self.output_v = tk.StringVar()

        self.output_b = ttk.Button(self.fileframe, text='Output', command=self.setoutputpath)
        self.output_e = ttk.Entry(self.fileframe, textvariable=self.output_v,width=80)

        self.output_b.grid(column=0, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.output_e.grid(column=1, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))

        # ---

        self.paramsframe = ttk.Frame(self.mainframe, padding='3 3 3 3')
        self.paramsframe.grid(column=0, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))

        self.base_tr_v = tk.StringVar()
        self.tgt_tr_v = tk.StringVar()
        self.new_tr_v = tk.StringVar()
        self.base_tr_e = ttk.Combobox(self.paramsframe, textvariable = self.base_tr_v)
        self.tgt_tr_e = ttk.Combobox(self.paramsframe, textvariable = self.tgt_tr_v)
        self.new_tr_e = ttk.Entry(self.paramsframe, textvariable = self.new_tr_v)
        self.base_tr_l = ttk.Label(self.paramsframe, text='Base')
        self.tgt_tr_l = ttk.Label(self.paramsframe, text='Target')
        self.new_tr_l = ttk.Label(self.paramsframe, text='New')

        self.base_tr_l.grid(column=0, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.base_tr_e.grid(column=1, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.tgt_tr_l.grid(column=2,  row=0, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.tgt_tr_e.grid(column=3,  row=0, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.new_tr_l.grid(column=4,  row=0, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.new_tr_e.grid(column=5,  row=0, sticky = (tk.N, tk.W, tk.E, tk.S))

        self.kp_start_v = tk.DoubleVar(value=0)
        self.kp_start_e = ttk.Entry(self.paramsframe, textvariable=self.kp_start_v)
        self.kp_start_l = ttk.Label(self.paramsframe, text='Start')

        self.kp_end_v = tk.DoubleVar(value=0)
        self.kp_end_e = ttk.Entry(self.paramsframe, textvariable=self.kp_end_v)
        self.kp_end_l = ttk.Label(self.paramsframe, text='End')

        self.kp_interval_v = tk.DoubleVar(value=5)
        self.kp_interval_e = ttk.Entry(self.paramsframe, textvariable=self.kp_interval_v)
        self.kp_interval_l = ttk.Label(self.paramsframe, text='Interval')
        
        
        self.kp_start_l.grid(column=0,  row=1, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.kp_start_e.grid(column=1,  row=1, sticky = (tk.N, tk.W, tk.E, tk.S))

        self.kp_end_l.grid(column=2,  row=1, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.kp_end_e.grid(column=3,  row=1, sticky = (tk.N, tk.W, tk.E, tk.S))

        self.kp_interval_l.grid(column=4,  row=1, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.kp_interval_e.grid(column=5,  row=1, sticky = (tk.N, tk.W, tk.E, tk.S))

        self.ratio_v = tk.DoubleVar(value=0.5)
        self.ratio_e = ttk.Entry(self.paramsframe, textvariable=self.ratio_v)
        self.ratio_l = ttk.Label(self.paramsframe, text='Ratio')
        
        self.ratio_l.grid(column=0,  row=2, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.ratio_e.grid(column=1,  row=2, sticky = (tk.N, tk.W, tk.E, tk.S))

        # ---
        
        self.ctrlframe = ttk.Frame(self.mainframe, padding='3 3 3 3')
        self.ctrlframe.grid(column=0, row=2, sticky = (tk.N, tk.W, tk.E, tk.S))
        
        self.doit_b = ttk.Button(self.ctrlframe, text='Do It', command=self.doit)
        self.doit_b.grid(column=0,  row=0, sticky = (tk.N, tk.W, tk.E, tk.S))

        
    def closewindow(self):
        self.master.withdraw()
    def sendtopmost(self, event=None):
        self.master.lift()
        self.master.focus_force()
    def setoutputpath(self):
        path = filedialog.asksaveasfilename(initialdir=self.output_v.get())
        if path != '':
            self.output_v.set(path)
    def make_trackkeylist(self):

        # Track構文で記述した他軌道
        owot_keys = []
        
        for parent_tr in self.trackcontrol.track.keys():
            for child_tr in self.trackcontrol.track[parent_tr]['othertrack'].keys():
                owot_keys.append('@OT_{:s}@_{:s}'.format(parent_tr,child_tr))

        trackkeylist = tuple(self.trackcontrol.track.keys())\
            +tuple(self.trackcontrol.pointsequence_track.track.keys())\
            +tuple(owot_keys)

        self.base_tr_e['values'] = tuple(self.trackcontrol.track.keys())
        self.tgt_tr_e['values'] = trackkeylist
    def doit(self):
        result_elem,result_map = self.trackcontrol.generate_mediantrack(self.base_tr_v.get(),\
                                                                        self.tgt_tr_v.get(),\
                                                                        self.new_tr_v.get(),\
                                                                        self.ratio_v.get(),\
                                                                        self.kp_start_v.get(),\
                                                                        self.kp_end_v.get(),\
                                                                        self.kp_interval_v.get())

        with open(self.output_v.get(), 'w') as fp:
            fp.write(result_map)
        
