'''
    Copyright 2021-2022 konawasabi

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

import sys
import pathlib
import os
import webbrowser

import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as filedialog
import tkinter.simpledialog as simpledialog
import tkinter.font as font

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import rcParams
import matplotlib.gridspec
from PIL import Image
import numpy as np


rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Hiragino Sans', 'Yu Gothic', 'Meirio', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']

from . import track_control
from . import drawcursor
from . import backimg
from . import measure

class Catcher: # tkinter内で起きた例外をキャッチする
    def __init__(self, func, subst, widget):
        self.func = func
        self.subst = subst
        self.widget = widget

    def __call__(self, *args):
        try:
            if self.subst:
               args = self.subst(*args)
            return self.func(*args)
        except Exception as e:
            if not __debug__: # デバッグモード(-O)なら素通し。pdbが起動する
                raise e
            else:
                print(e) # 通常モードならダイアログ表示
                tk.messagebox.showinfo(message=e)

class mainwindow(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding='3 3 3 3')
        self.master.title('Tsutsuji')
        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        master.protocol('WM_DELETE_WINDOW', self.ask_quit)
        
        self.backimgctrl = backimg.BackImgControl(self)
        self.cursor = drawcursor.cursor(self)
        self.measurewindow = measure.interface(self)

        self.trackcontrol = track_control.TrackControl()
        
        self.create_widgets()
        self.create_menubar()
    def create_widgets(self):
        font_title = font.Font(weight='bold',size=10)
        
        # プロットフレーム
        self.canvas_frame = ttk.Frame(self, padding='3 3 3 3')
        self.canvas_frame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        self.fig_plane = plt.figure(figsize=(9,7),tight_layout=True)
        gs1 = self.fig_plane.add_gridspec(nrows=1,ncols=1)
        self.ax_plane = self.fig_plane.add_subplot(gs1[0])
        
        self.plt_canvas_base = tk.Canvas(self.canvas_frame, bg="white", width=900, height=700)
        self.plt_canvas_base.grid(row = 0, column = 0)
        
        def on_canvas_resize(event):
            self.plt_canvas_base.itemconfigure(self.fig_frame_id, width=event.width, height=event.height)
            #print(event)
        
        self.fig_frame = tk.Frame(self.plt_canvas_base)
        self.fig_frame_id = self.plt_canvas_base.create_window((0, 0), window=self.fig_frame, anchor="nw")
        self.fig_frame.columnconfigure(0, weight=1)
        self.fig_frame.rowconfigure(0, weight=1)
        self.plt_canvas_base.bind("<Configure>", on_canvas_resize)
        
        self.fig_canvas = FigureCanvasTkAgg(self.fig_plane, master=self.fig_frame)
        self.fig_canvas.draw()
        self.fig_canvas.get_tk_widget().grid(row=0, column=0, sticky='news')
        
        self.canvas_frame.columnconfigure(0, weight=1)
        #self.canvas_frame.columnconfigure(1, weight=1)
        self.canvas_frame.rowconfigure(0, weight=1)
        #self.canvas_frame.rowconfigure(1, weight=1)
        
        #ボタンフレーム
        self.button_frame = ttk.Frame(self, padding='3 3 3 3')
        self.button_frame.grid(column=1, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        self.replot_btn = ttk.Button(self.button_frame, text="Replot", command = self.drawall)
        self.replot_btn.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E))
        
        self.plotarea_frame = ttk.Frame(self.button_frame, padding='3 3 3 3')
        self.plotarea_frame.grid(column=0, row=1, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        self.viewpos_v = [tk.DoubleVar(value=0),tk.DoubleVar(value=0)]
        self.viewp_scale_v = tk.DoubleVar(value=1000)
        self.view_whole_v = tk.StringVar()
        self.view_whole_v.set('False')
        
        self.viewp_x_l = ttk.Label(self.plotarea_frame, text='x')
        self.viewp_y_l = ttk.Label(self.plotarea_frame, text='y')
        self.viewp_sc_l = ttk.Label(self.plotarea_frame, text='scale')
        
        self.viewp_x_l.grid(column=0, row=0, sticky=(tk.E,tk.W))
        self.viewp_y_l.grid(column=2, row=0, sticky=(tk.E,tk.W))
        self.viewp_sc_l.grid(column=0, row=1, sticky=(tk.E,tk.W))
        
        self.viewp_x_e = ttk.Entry(self.plotarea_frame, textvariable=self.viewpos_v[0],width=5)
        self.viewp_y_e = ttk.Entry(self.plotarea_frame, textvariable=self.viewpos_v[1],width=5)
        self.viewp_sc_e = ttk.Entry(self.plotarea_frame, textvariable=self.viewp_scale_v,width=5)
        self.view_whole_e = ttk.Checkbutton(self.plotarea_frame, text='Whole', variable=self.view_whole_v, onvalue='True', offvalue='False')
        
        self.viewp_x_e.grid(column=1, row=0, sticky=(tk.E,tk.W))
        self.viewp_y_e.grid(column=3, row=0, sticky=(tk.E,tk.W))
        self.viewp_sc_e.grid(column=1, row=1, sticky=(tk.E,tk.W))
        self.view_whole_e.grid(column=0, row=2, sticky=(tk.E,tk.W))
        
        self.measure_btn = ttk.Button(self.button_frame, text="measure", command = self.measure)
        self.measure_btn.grid(column=0, row=2, sticky=(tk.N, tk.W, tk.E))

        self.printtracks_btn = ttk.Button(self.button_frame, text="P. Tracks", command = self.trackcontrol.dump_trackdata)
        self.printtracks_btn.grid(column=0, row=3, sticky=(tk.N, tk.W, tk.E))
        
        self.printpos_btn = ttk.Button(self.button_frame, text="P. Pos", command = self.draw_tracks_cp)#trackcontrol.dump_trackpos)
        self.printpos_btn.grid(column=0, row=4, sticky=(tk.N, tk.W, tk.E))
        
        # ウィンドウリサイズに対する設定
        self.columnconfigure(0, weight=1)
        #self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
    def create_menubar(self):
        self.master.option_add('*tearOff', False)
        
        self.menubar = tk.Menu(self.master)
        
        self.menu_file = tk.Menu(self.menubar)
        self.menu_backimg = tk.Menu(self.menubar)
        self.menu_help = tk.Menu(self.menubar)
        
        self.menubar.add_cascade(menu=self.menu_file, label='ファイル')
        self.menubar.add_cascade(menu=self.menu_backimg, label='背景画像')
        self.menubar.add_cascade(menu=self.menu_help, label='ヘルプ')
        
        self.menu_file.add_command(label='開く...', command=self.opencfg, accelerator='Control+O')
        self.menu_file.add_separator()
        self.menu_file.add_command(label='終了', command=self.ask_quit, accelerator='Alt+F4')
        
        self.menu_backimg.add_command(label='Window...', command=self.backimgctrl.create_window)
        self.menu_backimg.add_separator()
        self.menu_backimg.add_command(label='Load...', command=None)
        self.menu_backimg.add_command(label='Save...', command=None)
        
        self.menu_help.add_command(label='ヘルプ...', command=None)
        self.menu_help.add_command(label='Tsutsujiについて...', command=None)
        
        self.master['menu'] = self.menubar
    def ask_quit(self, event=None, ask=True):
        if ask:
            if tk.messagebox.askyesno(message='Tsutsuji を終了しますか？'):
                self.quit()
        else:
            self.quit()
    def opencfg(self, event=None):
        inputdir = filedialog.askopenfilename()
        self.trackcontrol.loadcfg(inputdir)
        self.trackcontrol.loadmap()
        self.drawall()
    def draw2dplot(self):
        self.ax_plane.cla()
        self.trackcontrol.plot2d(self.ax_plane)
        self.fig_canvas.draw()
    def drawall(self):
        self.ax_plane.cla()
        self.trackcontrol.plot2d(self.ax_plane)
        
        for i in self.backimgctrl.imgs.keys():
            self.backimgctrl.imgs[i].show(self.ax_plane)

        self.measurewindow.drawall()
            
        if self.view_whole_v.get() == 'True':
            imgarea = self.backimgctrl.imgsarea()
            imgarea = self.trackcontrol.drawarea(imgarea)
            
            self.ax_plane.set_xlim(imgarea[0],imgarea[1])
            self.ax_plane.set_ylim(imgarea[2],imgarea[3])
        else:
            center = [self.viewpos_v[0].get(),self.viewpos_v[1].get()]
            #windowratio = self.ax_plane.bbox.height/self.ax_plane.bbox.width # 平面図のアスペクト比を取得
            windowratio = 7/9
            scalex = self.viewp_scale_v.get()
            scaley = windowratio * scalex
            
            self.ax_plane.set_xlim(center[0]-scalex/2, center[0]+scalex/2)
            self.ax_plane.set_ylim(center[1]-scaley/2, center[1]+scaley/2)
        self.ax_plane.invert_yaxis()
        self.fig_canvas.draw()
    def measure(self):
        self.measurewindow.create_widgets()
    def draw_tracks_cp(self):
        self.trackcontrol.plot_controlpoints(self.ax_plane,owntrack='down')
        self.fig_canvas.draw()
    def get_relativepos_rad(self):
        self.trackcontrol.relativepoint(owntrack='down')
        self.trackcontrol.relativeradius(owntrack='down')
        self.trackcontrol.relativeradius_cp(owntrack='down')
        for tr in [i for i in tc.conf.track_keys if i != 'down']:
            for data in tc.rel_track_radius_cp[tr]:
                print('{:.2f};'.format(data[0]))
                print('Track[\''+tr+'\'].X.Interpolate({:.2f},{:.2f});'.format(data[3],data[2]))
    
def main():
    if not __debug__:
        # エラーが発生した場合、デバッガを起動 https://gist.github.com/podhmo/5964702e7471ccaba969105468291efa
        def info(type, value, tb):
            if hasattr(sys, "ps1") or not sys.stderr.isatty():
                # You are in interactive mode or don't have a tty-like
                # device, so call the default hook
                sys.__excepthook__(type, value, tb)
            else:
                import traceback, pdb

                # You are NOT in interactive mode; print the exception...
                traceback.print_exception(type, value, tb)
                # ...then start the debugger in post-mortem mode
                pdb.pm()
        import sys
        sys.excepthook = info
        print('Debug mode')
    
    tk.CallWrapper = Catcher
    root = tk.Tk()
    app = mainwindow(master=root)
    app.mainloop()
