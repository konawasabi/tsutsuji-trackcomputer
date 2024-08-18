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
import re

from kobushi import trackcoordinate

from . import drawcursor
'''
from . import solver
from . import math
from . import curvetrackplot
'''

class Interface():
    def __init__(self,mainwindow):
        self.mainwindow = mainwindow
        self.master = None
        #self.trackcontrol = self.mainwindow.trackcontrol
        self.cursorlist_column = ('Track', 'Distance', 'Height', 'Gradient')
    def create_window(self):
        if self.master is None:
            self.master = tk.Toplevel(self.mainwindow)
            self.master.title('Measure (Height)')
            self.master.protocol('WM_DELETE_WINDOW', self.closewindow)
            self.master.columnconfigure(0, weight=1)
            self.master.rowconfigure(0, weight=1)
            
            self.mainframe = ttk.Frame(self.master, padding = '3 3 3 3')
            self.mainframe.columnconfigure(0, weight=1)
            self.mainframe.rowconfigure(0, weight=1)
            self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
            
            self.create_widgets()
        else:
            self.sendtopmost()
    def create_widgets(self):
        self.cursorlist = ttk.Treeview(self.mainframe, column=self.cursorlist_column)
        self.cursorlist.column('#0',width=10)
        self.cursorlist.column('Track',width=80)
        self.cursorlist.column('Distance',width=80)
        self.cursorlist.column('Height',width=80)
        self.cursorlist.column('Gradient',width=80)
        self.cursorlist.heading('#0',text='ID')
        self.cursorlist.heading('Track',text='Track')
        self.cursorlist.heading('Distance',text='Distance')
        self.cursorlist.heading('Height',text='Height')
        self.cursorlist.heading('Gradient',text='Gradient')
        
        self.cursorlist.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

        self.button_frame = ttk.Frame(self.mainframe, padding='3 3 3 3')
        self.button_frame.grid(column=0, row=1,sticky=(tk.E, tk.W))

        self.add_b = ttk.Button(self.button_frame, text='Add', command=self.addcursor)
        self.del_b = ttk.Button(self.button_frame, text='Delete', command=self.deletecursor)

        self.add_b.grid(column=0, row=0,sticky=(tk.N, tk.E, tk.W))
        self.del_b.grid(column=1, row=0,sticky=(tk.N, tk.E, tk.W))
        
    def closewindow(self):
        if self.master is not None:
            self.master.withdraw()
            self.master = None
    def sendtopmost(self,event=None):
        self.master.lift()
        self.master.focus_force()
    def addcursor(self):
        self.cursorlist.insert('','end',values=('@absolute',255,255,255))
    def deletecursor(self):
        selected = self.cursorlist.focus()
        if len(selected)>0:
            self.cursorlist.delete(selected)
