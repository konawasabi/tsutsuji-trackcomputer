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

from . import heightmeasure
from . import backimg_height

class HeightWindow():
    def __init__(self,mainwindow):
        self.mainwindow = mainwindow
        self.master = None
        self.trackcontrol = self.mainwindow.trackcontrol
        self.measureUI = heightmeasure.Interface(self)
        self.backimg = backimg_height.BackImgControl_Height(self)

        self.distance_lim_v = [tk.DoubleVar(value=0),tk.DoubleVar(value=0)]
        self.height_lim_v = [tk.DoubleVar(value=0),tk.DoubleVar(value=0)]
        self.dlim_auto_v = tk.BooleanVar(value=True)
        self.hlim_auto_v = tk.BooleanVar(value=True)
        self.menu_height = None

        self.menu_disable_list = ('Measure...', 'Backimg...', 'Load Backimg...', 'Save Backimg...')

        self.plot_marker_ctrl_v = {}
        position = 0
        for val in ['radius','gradient','supplemental_cp','track']:
            self.plot_marker_ctrl_v[val] = tk.BooleanVar(value=False)
    def create_window(self):
        if self.master is None:
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

            if self.menu_height is not None:
                for label in self.menu_disable_list:
                    self.menu_height.entryconfigure(label, state='active')
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
        
        self.dlim_auto_ent = ttk.Checkbutton(self.plotarea_val_frame, text='', variable=self.dlim_auto_v, onvalue=True, offvalue=False, command=lambda: self.setautolim(self.dlim_auto_v))
        self.hlim_auto_ent = ttk.Checkbutton(self.plotarea_val_frame, text='', variable=self.hlim_auto_v, onvalue=True, offvalue=False, command=lambda: self.setautolim(self.hlim_auto_v))
        
        self.dmin_ent.grid(column=1, row=1, sticky=(tk.E,tk.W))
        self.dmax_ent.grid(column=2, row=1, sticky=(tk.E,tk.W))
        self.hmin_ent.grid(column=1, row=2, sticky=(tk.E,tk.W))
        self.hmax_ent.grid(column=2, row=2, sticky=(tk.E,tk.W))
        self.dlim_auto_ent.grid(column=3, row=1, sticky=(tk.E,tk.W))
        self.hlim_auto_ent.grid(column=3, row=2, sticky=(tk.E,tk.W))

        # ---

        self.plotmove_frame = ttk.Frame(self.plotarea_frame, padding='3 3 3 3')
        self.plotmove_frame.grid(column=0, row=1, sticky=(tk.N, tk.W, tk.E, tk.S))

        self.plotmove_btn_left = ttk.Button(self.plotmove_frame, text="←", command = lambda: self.move_xy(-1,0))
        self.plotmove_btn_right = ttk.Button(self.plotmove_frame, text="→", command = lambda: self.move_xy(1,0))
        
        self.plotmove_btn_left.grid(column=0, row=0, sticky=(tk.E,tk.W))
        self.plotmove_btn_right.grid(column=1, row=0, sticky=(tk.E,tk.W))
        
        # ---

        self.plotarea_symbol_frame = ttk.Labelframe(self.plotarea_frame, padding='3 3 3 3', text = 'Symbols')
        self.plotarea_symbol_frame.grid(column=0, row=2, sticky=(tk.E,tk.W))
        self.plot_marker_ctrl_w = {}
        position = 0
        for val in ['radius','gradient','supplemental_cp','track']:
            self.plot_marker_ctrl_w = ttk.Checkbutton(self.plotarea_symbol_frame, text=val, variable=self.plot_marker_ctrl_v[val], onvalue=True, offvalue=False)
            self.plot_marker_ctrl_w.grid(column=0, row=position, sticky=(tk.E,tk.W))
            position +=1

        # ---

        self.backimg_b = ttk.Button(self.button_frame, text='BackImg.', command = self.backimg.create_window)
        self.backimg_b.grid(column=0, row=2,sticky=(tk.E,tk.W))
        
        self.measure_b = ttk.Button(self.button_frame, text='Measure', command = self.measureUI.create_window)
        self.measure_b.grid(column=0, row=3,sticky=(tk.E,tk.W))

        # ---
        
        self.drawall()
    def closewindow(self):
        self.master.withdraw()
        self.measureUI.closewindow()
        self.master = None
        if self.menu_height is not None:
            for label in self.menu_disable_list:
                self.menu_height.entryconfigure(label, state='disabled')
    def sendtopmost(self,event=None):
        self.master.lift()
        self.master.focus_force()
    def setautolim(self, val):
        if val.get() == 'True':
            self.drawall()
    def move_xy(self, x, y):
        if self.dlim_auto_v.get() == False:
            xlim = (self.distance_lim_v[0].get(), self.distance_lim_v[1].get())
            delta = (xlim[1]-xlim[0])/5*x
            self.distance_lim_v[0].set(xlim[0]+delta)
            self.distance_lim_v[1].set(xlim[1]+delta)
            self.drawall()
    def drawall(self):
        if self.master is not None:
            self.ax_height.cla()
            self.trackcontrol.plot2d_height(self.ax_height)
            self.ax_height.set_xlabel('distance [m]')
            self.ax_height.set_ylabel('height [m]')

            # 描画範囲Autoでない場合
            if self.dlim_auto_v.get() == False:
                self.ax_height.set_xlim(self.distance_lim_v[0].get(), self.distance_lim_v[1].get())
            else:
                self.ax_height.set_xlim()
                xlim = self.ax_height.get_xlim()
                for ix in (0,1):
                    self.distance_lim_v[ix].set(float(np.floor(xlim[ix])))
            if self.hlim_auto_v.get() == False:
                self.ax_height.set_ylim(self.height_lim_v[0].get(), self.height_lim_v[1].get())
            else:
                self.ax_height.set_ylim()
                ylim = self.ax_height.get_ylim()
                for ix in (0,1):
                    self.height_lim_v[ix].set(float(np.floor(ylim[ix])))

            # 軌道要素シンボル
            
            for key in self.plot_marker_ctrl_v.keys():
                if self.plot_marker_ctrl_v[key].get():
                    self.trackcontrol.plot_symbols_height(self.ax_height,key)

            # カーソル
            self.measureUI.replotCursors()

            # 背景画像
            plotsize = self.fig_height.get_size_inches()
            for i in self.backimg.imgs.keys():
                self.backimg.imgs[i].show(self.ax_height,as_ratio=plotsize[1]/plotsize[0])
            
            self.fig_canvas.draw()
    def reloadcfg(self):
        self.measureUI.reload_trackkeys()
    def create_menu(self):
        if self.menu_height is None:
            self.menu_height = self.mainwindow.menu_height
            self.menu_height.add_command(label='Display...', command=self.create_window)
            self.menu_height.add_command(label='Measure...', command=self.measureUI.create_window)
            self.menu_height.add_separator()
            self.menu_height.add_command(label='Backimg...', command=self.backimg.create_window)
            self.menu_height.add_command(label='Load Backimg...', command=self.backimg.load_setting)
            self.menu_height.add_command(label='Save Backimg...', command=self.backimg.save_setting)

            for label in self.menu_disable_list:
                self.menu_height.entryconfigure(label, state='disabled')
        
