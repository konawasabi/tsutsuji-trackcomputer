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

class HeightWindow():
    def __init__(self,mainwindow):
        self.mainwindow = mainwindow
        self.master = None
        self.trackcontrol = self.mainwindow.trackcontrol

        self.distance_lim_v = [tk.DoubleVar(value=0),tk.DoubleVar(value=0)]
        self.height_lim_v = [tk.DoubleVar(value=0),tk.DoubleVar(value=0)]
        self.dlim_auto_v = tk.StringVar()
        self.dlim_auto_v.set('True')
        self.hlim_auto_v = tk.StringVar()
        self.hlim_auto_v.set('True')
    def create_window(self):
        if self.master == None:
            self.master = tk.Toplevel(self.mainwindow)
            self.mainframe = ttk.Frame(self.master, padding = '3 3 3 3')
            self.mainframe.columnconfigure(0, weight=1)
            self.mainframe.rowconfigure(0, weight=1)
            self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
            self.master.title('Height')
            self.master.protocol('WM_DELETE_WINDOW', self.closewindow)
            self.master.columnconfigure(0, weight=1)
            self.master.rowconfigure(0, weight=1)

            self.create_widgets()
        else:
            self.sendtopmost()
    def create_widgets(self):
        self.canvas_frame = ttk.Frame(self.mainframe, padding='3 3 3 3')
        self.canvas_frame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        self.fig_height = plt.figure(figsize=(8,5),tight_layout=True)
        gs1 = self.fig_height.add_gridspec(nrows=1,ncols=1)
        self.ax_height = self.fig_height.add_subplot(gs1[0])
        
        self.plt_canvas_base = tk.Canvas(self.canvas_frame, bg="white", width=800, height=500)
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

        # --- ボタンフレーム
        self.button_frame = ttk.Frame(self.mainframe, padding='3 3 3 3')
        self.button_frame.grid(column=1, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

        self.replot_btn = ttk.Button(self.button_frame, text="Replot", command = self.drawall)
        self.replot_btn.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E))

        # --- プロット範囲フレーム

        self.plotarea_frame = ttk.Labelframe(self.button_frame, padding='3 3 3 3', text = 'Plot control')
        self.plotarea_frame.grid(column=0, row=1, sticky=(tk.N, tk.W, tk.E, tk.S))

        self.plotarea_val_frame = ttk.Frame(self.plotarea_frame, padding='3 3 3 3')
        self.plotarea_val_frame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        self.min_l = ttk.Label(self.plotarea_val_frame, text='min.')
        self.max_l = ttk.Label(self.plotarea_val_frame, text='max.')
        self.d_l = ttk.Label(self.plotarea_val_frame, text='dist.')
        self.h_l = ttk.Label(self.plotarea_val_frame, text='ht.')
        self.auto_l = ttk.Label(self.plotarea_val_frame, text='auto')
        
        self.min_l.grid(column=1, row=0, sticky=(tk.E,tk.W))
        self.max_l.grid(column=2, row=0, sticky=(tk.E,tk.W))
        self.d_l.grid(column=0, row=1, sticky=(tk.E,tk.W))
        self.h_l.grid(column=0, row=2, sticky=(tk.E,tk.W))
        self.auto_l.grid(column=3, row=0, sticky=(tk.E,tk.W))

        self.dmin_ent = ttk.Entry(self.plotarea_val_frame, textvariable=self.distance_lim_v[0],width=5)
        self.dmax_ent = ttk.Entry(self.plotarea_val_frame, textvariable=self.distance_lim_v[1],width=5)
        self.hmin_ent = ttk.Entry(self.plotarea_val_frame, textvariable=self.height_lim_v[0],width=5)
        self.hmax_ent = ttk.Entry(self.plotarea_val_frame, textvariable=self.height_lim_v[1],width=5)
        
        self.dlim_auto_ent = ttk.Checkbutton(self.plotarea_val_frame, text='', variable=self.dlim_auto_v, onvalue='True', offvalue='False', command=lambda: self.setautolim(self.dlim_auto_v))
        self.hlim_auto_ent = ttk.Checkbutton(self.plotarea_val_frame, text='', variable=self.hlim_auto_v, onvalue='True', offvalue='False', command=lambda: self.setautolim(self.hlim_auto_v))
        
        self.dmin_ent.grid(column=1, row=1, sticky=(tk.E,tk.W))
        self.dmax_ent.grid(column=2, row=1, sticky=(tk.E,tk.W))
        self.hmin_ent.grid(column=1, row=2, sticky=(tk.E,tk.W))
        self.hmax_ent.grid(column=2, row=2, sticky=(tk.E,tk.W))
        self.dlim_auto_ent.grid(column=3, row=1, sticky=(tk.E,tk.W))
        self.hlim_auto_ent.grid(column=3, row=2, sticky=(tk.E,tk.W))

        # ---
        
        self.drawall()
    def closewindow(self):
        self.master.withdraw()
        self.master = None
    def sendtopmost(self,event=None):
        self.master.lift()
        self.master.focus_force()
    def setautolim(self, val):
        if val.get() == 'True':
            self.drawall()
    def drawall(self):
        if self.master is not None:
            self.ax_height.cla()
            self.trackcontrol.plot2d_height(self.ax_height)
            self.ax_height.set_xlabel('distance [m]')
            self.ax_height.set_ylabel('height [m]')
            if self.dlim_auto_v.get() == 'False':
                self.ax_height.set_xlim(self.distance_lim_v[0].get(), self.distance_lim_v[1].get())
            else:
                self.ax_height.set_xlim()
                xlim = self.ax_height.get_xlim()
                for ix in (0,1):
                    self.distance_lim_v[ix].set(float(xlim[ix]))
            if self.hlim_auto_v.get() == 'False':
                self.ax_height.set_ylim(self.height_lim_v[0].get(), self.height_lim_v[1].get())
            else:
                self.ax_height.set_ylim()
                ylim = self.ax_height.get_ylim()
                for ix in (0,1):
                    self.height_lim_v[ix].set(float(ylim[ix]))
            self.fig_canvas.draw()
        
