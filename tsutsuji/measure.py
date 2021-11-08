'''
    Copyright 2021 konawasabi

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''

import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import ttk

class measure():
    def __init__(self):
        pass

class interface():
    class unit():
        def __init__(self,name,parent,row):
            self.p = parent
            self.name = name
            self.create_widgets(row)
        def create_widgets(self,row):
            self.name_l = ttk.Label(self.p, text=self.name)
            self.name_l.grid(column=0, row=row, sticky=(tk.E,tk.W))
            
            self.values = [tk.DoubleVar(value=0),tk.DoubleVar(value=0),tk.DoubleVar(value=0),tk.StringVar(value='')]
            self.x_e = ttk.Entry(self.p, textvariable=self.values[0],width=5)
            self.y_e = ttk.Entry(self.p, textvariable=self.values[1],width=5)
            self.theta_e = ttk.Entry(self.p, textvariable=self.values[2],width=5)
            self.track_e = ttk.Entry(self.p, textvariable=self.values[3],width=5)
            
            self.setcursor_b = ttk.Button(self.p, text="Set", command=None, width=3)
            
            self.cursormode_v = tk.StringVar(value='absolute')
            self.cursormode_b_abs = ttk.Radiobutton(self.p,text='', variable=self.cursormode_v, value='absolute',command=self.printmode)
            self.cursormode_b_tr  = ttk.Radiobutton(self.p,text='' , variable=self.cursormode_v, value='track',command=self.printmode)
            
            self.x_e.grid(column=1, row=row, sticky=(tk.E,tk.W))
            self.y_e.grid(column=2, row=row, sticky=(tk.E,tk.W))
            self.theta_e.grid(column=3, row=row, sticky=(tk.E,tk.W))
            self.track_e.grid(column=4, row=row, sticky=(tk.E,tk.W))
            self.setcursor_b.grid(column=5, row=row, sticky=(tk.E,tk.W))
            self.cursormode_b_abs.grid(column=6, row=row, sticky=(tk.E,tk.W))
            self.cursormode_b_tr.grid(column=7, row=row, sticky=(tk.E,tk.W))
        def printmode(self):
            print(self.name,self.cursormode_v.get())
            
    def __init__(self,mainwindow):
        self.mainwindow = mainwindow
        self.create_widgets()
    def create_widgets(self):
        self.master = tk.Toplevel(self.mainwindow)
        self.mainframe = ttk.Frame(self.master, padding='3 3 3 3')
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)
        self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        self.master.title('Measure')

        self.position_f = ttk.Frame(self.mainframe, padding='3 3 3 3')
        self.position_f.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        self.position_label = {}
        pos = 1
        for i in ['x','y','dir','track',' ','abs','trk']:
            self.position_label[i] = ttk.Label(self.position_f, text=i)
            self.position_label[i].grid(column=pos, row=0, sticky=(tk.E,tk.W))
            pos+=1
        self.cursor_A = self.unit('A',self.position_f,1)
        self.cursor_B = self.unit('B',self.position_f,2)
