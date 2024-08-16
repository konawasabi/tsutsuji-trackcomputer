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
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import rcParams
import matplotlib.gridspec
from PIL import Image
import numpy as np
import tkinter as tk
from tkinter import ttk

class interface():
    def __init__(self,mainwindow):
        self.mainwindow = mainwindow
        self.master = None
    def create_window(self):
        if self.master == None:
            self.master = tk.Toplevel(self.mainwindow)
            self.mainframe = ttk.Frame(self.master, padding = '3 3 3 3')
            self.mainframe.columnconfigure(0, weight=1)
            self.mainframe.rowconfigure(0, weight=1)
            self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
            self.master.title('Height')
            self.master.protocol('WM_DELETE_WINDOW', self.closewindow)

            self.create_widgets()
    def create_widgets(self):
        self.canvas_frame = ttk.Frame(self.mainframe, padding='3 3 3 3')
        self.canvas_frame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        self.fig_height = plt.figure(figsize=(9,7),tight_layout=True)
        gs1 = self.fig_height.add_gridspec(nrows=1,ncols=1)
        self.ax_height = self.fig_height.add_subplot(gs1[0])
        
        self.plt_canvas_base = tk.Canvas(self.canvas_frame, bg="white", width=900, height=700)
        self.plt_canvas_base.grid(row = 0, column = 0, sticky=(tk.N, tk.W, tk.E, tk.S))

        def on_canvas_resize(event):
            self.plt_canvas_base.itemconfigure(self.fig_frame_id, width=event.width, height=event.height)
            
        self.fig_frame = tk.Frame(self.plt_canvas_base)
        self.fig_frame_id = self.plt_canvas_base.create_window((0, 0), window=self.fig_frame, anchor="nw")
        self.fig_frame.columnconfigure(0, weight=1)
        self.fig_frame.rowconfigure(0, weight=1)
        self.plt_canvas_base.bind("<Configure>", on_canvas_resize)
        
        self.fig_canvas = FigureCanvasTkAgg(self.fig_height, master=self.fig_frame)
        self.fig_canvas.draw()
        self.fig_canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        self.canvas_frame.columnconfigure(0, weight=1)
        self.canvas_frame.rowconfigure(0, weight=1)
    def closewindow(self):
        self.master.withdraw()
        self.master = None
        
