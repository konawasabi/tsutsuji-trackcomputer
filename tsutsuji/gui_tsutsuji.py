#
#    Copyright 2021-2023 konawasabi
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

import sys
import pathlib
import os
import webbrowser
import argparse

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
from ._version import __version__
from . import trackwindow

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
        self.parent = master
        super().__init__(master, padding='3 3 3 3')
        self.master.title('Tsutsuji')
        self.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        master.protocol('WM_DELETE_WINDOW', self.ask_quit)
        
        self.backimgctrl = backimg.BackImgControl(self)
        self.cursor = drawcursor.cursor(self)
        self.measurewindow = measure.interface(self)
        self.trackwindow = trackwindow.TrackWindow(self)

        self.trackcontrol = track_control.TrackControl()

        self.staticmapctrl = backimg.TileMapControl(self)
        
        self.create_widgets()
        self.create_menubar()
        self.bind_keyevent()
    def create_widgets(self):
        font_title = font.Font(weight='bold',size=10)
        
        # プロットフレーム
        self.canvas_frame = ttk.Frame(self, padding='3 3 3 3')
        self.canvas_frame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        self.fig_plane = plt.figure(figsize=(9,7),tight_layout=True)
        gs1 = self.fig_plane.add_gridspec(nrows=1,ncols=1)
        self.ax_plane = self.fig_plane.add_subplot(gs1[0])
        
        self.plt_canvas_base = tk.Canvas(self.canvas_frame, bg="white", width=900, height=700)
        self.plt_canvas_base.grid(row = 0, column = 0, sticky=(tk.N, tk.W, tk.E, tk.S))

        def on_canvas_resize(event):
            #print(event, self.fig_plane.get_size_inches())
            self.plt_canvas_base.itemconfigure(self.fig_frame_id, width=event.width, height=event.height)
            
        self.fig_frame = tk.Frame(self.plt_canvas_base)
        self.fig_frame_id = self.plt_canvas_base.create_window((0, 0), window=self.fig_frame, anchor="nw")
        self.fig_frame.columnconfigure(0, weight=1)
        self.fig_frame.rowconfigure(0, weight=1)
        self.plt_canvas_base.bind("<Configure>", on_canvas_resize)
        
        self.fig_canvas = FigureCanvasTkAgg(self.fig_plane, master=self.fig_frame)
        self.fig_canvas.draw()
        self.fig_canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        self.canvas_frame.columnconfigure(0, weight=1)
        #self.canvas_frame.columnconfigure(1, weight=1)
        self.canvas_frame.rowconfigure(0, weight=1)
        #self.canvas_frame.rowconfigure(1, weight=1)
        
        #ボタンフレーム
        self.button_frame = ttk.Frame(self, padding='3 3 3 3')
        self.button_frame.grid(column=1, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

        # ---
        
        self.replot_btn = ttk.Button(self.button_frame, text="Replot", command = self.drawall)
        self.replot_btn.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E))
        
        self.plotarea_frame = ttk.Labelframe(self.button_frame, padding='3 3 3 3', text = 'Plot control')
        self.plotarea_frame.grid(column=0, row=1, sticky=(tk.N, tk.W, tk.E, tk.S))

        self.plotarea_val_frame = ttk.Frame(self.plotarea_frame, padding='3 3 3 3')
        self.plotarea_val_frame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        self.viewpos_v = [tk.DoubleVar(value=0),tk.DoubleVar(value=0)]
        self.viewp_scale_v = tk.DoubleVar(value=1000)
        self.view_whole_v = tk.StringVar()
        self.view_whole_v.set('False')
        self.aspectratio_v = tk.DoubleVar(value=1)
        
        self.viewp_x_l = ttk.Label(self.plotarea_val_frame, text='x')
        self.viewp_y_l = ttk.Label(self.plotarea_val_frame, text='y')
        self.viewp_sc_l = ttk.Label(self.plotarea_val_frame, text='scale')
        self.viewp_asr_l = ttk.Label(self.plotarea_val_frame, text='Y mag.')
        
        self.viewp_x_l.grid(column=0, row=0, sticky=(tk.E,tk.W))
        self.viewp_y_l.grid(column=2, row=0, sticky=(tk.E,tk.W))
        self.viewp_sc_l.grid(column=0, row=1, sticky=(tk.E,tk.W))
        self.viewp_asr_l.grid(column=2, row=1, sticky=(tk.E,tk.W))
        
        self.viewp_x_e = ttk.Entry(self.plotarea_val_frame, textvariable=self.viewpos_v[0],width=5)
        self.viewp_y_e = ttk.Entry(self.plotarea_val_frame, textvariable=self.viewpos_v[1],width=5)
        self.viewp_sc_e = ttk.Entry(self.plotarea_val_frame, textvariable=self.viewp_scale_v,width=5)
        self.view_whole_e = ttk.Checkbutton(self.plotarea_val_frame, text='Whole', variable=self.view_whole_v, onvalue='True', offvalue='False')
        self.viewp_asr_e = ttk.Entry(self.plotarea_val_frame, textvariable=self.aspectratio_v,width=5)
        
        self.viewp_x_e.grid(column=1, row=0, sticky=(tk.E,tk.W))
        self.viewp_y_e.grid(column=3, row=0, sticky=(tk.E,tk.W))
        self.viewp_sc_e.grid(column=1, row=1, sticky=(tk.E,tk.W))
        self.viewp_asr_e.grid(column=3, row=1, sticky=(tk.E,tk.W))
        self.view_whole_e.grid(column=0, row=3, sticky=(tk.E,tk.W))

        # ---
        
        self.plotmove_frame = ttk.Frame(self.plotarea_frame, padding='3 3 3 3')
        self.plotmove_frame.grid(column=0, row=1, sticky=(tk.N, tk.W, tk.E, tk.S))

        self.plotmove_btn_up = ttk.Button(self.plotmove_frame, text="↑", command = lambda: self.move_xy(0,-1))
        self.plotmove_btn_down = ttk.Button(self.plotmove_frame, text="↓", command = lambda: self.move_xy(0,1))
        self.plotmove_btn_left = ttk.Button(self.plotmove_frame, text="←", command = lambda: self.move_xy(-1,0))
        self.plotmove_btn_right = ttk.Button(self.plotmove_frame, text="→", command = lambda: self.move_xy(1,0))

        self.plotmove_btn_up.grid(column=1, row=0, sticky=(tk.E,tk.W))
        self.plotmove_btn_down.grid(column=1, row=2, sticky=(tk.E,tk.W))
        self.plotmove_btn_left.grid(column=0, row=1, sticky=(tk.E,tk.W))
        self.plotmove_btn_right.grid(column=2, row=1, sticky=(tk.E,tk.W))

        # ---

        self.plotarea_symbol_frame = ttk.Labelframe(self.plotarea_frame, padding='3 3 3 3', text = 'Symbols')
        self.plotarea_symbol_frame.grid(column=0, row=2, sticky=(tk.E,tk.W))
        self.plot_marker_ctrl = {}
        position = 0
        for val in ['radius','gradient','supplemental_cp','track']:
            self.plot_marker_ctrl[val] = {}
            self.plot_marker_ctrl[val]['variable'] = tk.BooleanVar(value=False)
            self.plot_marker_ctrl[val]['widget'] = ttk.Checkbutton(self.plotarea_symbol_frame, text=val, variable=self.plot_marker_ctrl[val]['variable'], onvalue=True, offvalue=False)
            self.plot_marker_ctrl[val]['widget'].grid(column=0, row=position, sticky=(tk.E,tk.W))
            position +=1

        # ---
        
        self.measure_btn = ttk.Button(self.button_frame, text="Measure", command = self.measure)
        self.measure_btn.grid(column=0, row=2, sticky=(tk.N, tk.W, tk.E, tk.S))

        if not __debug__:
            self.printtracks_btn = ttk.Button(self.button_frame, text="P. Tracks", command = self.trackcontrol.dump_trackdata)
            self.printtracks_btn.grid(column=0, row=4, sticky=(tk.N, tk.W, tk.E))

            self.printpos_btn = ttk.Button(self.button_frame, text="P. Pos", command = self.draw_tracks_cp)
            self.printpos_btn.grid(column=0, row=5, sticky=(tk.N, tk.W, tk.E))

            self.othertrack_btn = ttk.Button(self.button_frame, text="OtherTrack", command = self.get_othertrack)
            self.othertrack_btn.grid(column=0, row=6, sticky=(tk.N, tk.W, tk.E))

            '''
            self.statmap1_btn = ttk.Button(self.button_frame, text="statmap1", command = self.getmaptile)
            self.statmap1_btn.grid(column=0, row=7, sticky=(tk.N, tk.W, tk.E))
            '''

        self.getrelrad_btn = ttk.Button(self.button_frame, text="Generate", command = self.generate_output)
        self.getrelrad_btn.grid(column=0, row=10, sticky=(tk.E, tk.W, tk.S))
        self.button_frame.rowconfigure(10, weight=1)
        
        # ウィンドウリサイズに対する設定
        self.columnconfigure(0, weight=1)
        #self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # プロットウィンドウ描画
        self.drawall()
    def create_menubar(self):
        self.master.option_add('*tearOff', False)
        
        self.menubar = tk.Menu(self.master)
        
        self.menu_file = tk.Menu(self.menubar)
        self.menu_compute = tk.Menu(self.menubar)
        self.menu_option = tk.Menu(self.menubar)
        self.menu_help = tk.Menu(self.menubar)
        
        self.menubar.add_cascade(menu=self.menu_file, label='ファイル')
        self.menubar.add_cascade(menu=self.menu_compute, label='メイン処理')
        self.menubar.add_cascade(menu=self.menu_option, label='オプション')
        self.menubar.add_cascade(menu=self.menu_help, label='ヘルプ')
        
        self.menu_file.add_command(label='開く...', command=self.opencfg, accelerator='Control+O')
        self.menu_file.add_command(label='リロード', command=self.reloadcfg, accelerator='F5')
        self.menu_file.add_separator()
        self.menu_file.add_command(label='終了', command=self.ask_quit, accelerator='Alt+F4')

        self.menu_compute.add_command(label='Measure...', command=self.measure, accelerator='Control+M')
        self.menu_compute.add_command(label='Generate', command=self.generate_output, accelerator='Control+G')
        self.menu_compute.add_separator()
        self.menu_compute.add_command(label='Replot', command=self.drawall, accelerator='Return')
        
        self.menu_option.add_command(label='Backimg...', command=self.backimgctrl.create_window)
        self.menu_option.add_command(label='Load Backimg...', command=self.backimgctrl.load_setting)
        self.menu_option.add_command(label='Save Backimg...', command=self.backimgctrl.save_setting)
        self.menu_option.add_separator()
        self.menu_option.add_command(label='Maptile...', command=self.staticmapctrl.create_paramwindow, accelerator='Control+T')
        self.menu_option.add_command(label='Refresh Maptile', command=self.getmaptile, accelerator='Shift+Return')
        self.menu_option.add_command(label='Export Maptile...', command=self.staticmapctrl.export)
        self.menu_option.add_separator()
        self.menu_option.add_command(label='Track...', command=self.trackwindow.create_window)
        
        self.menu_help.add_command(label='ヘルプ...', command=self.open_webdocument)
        self.menu_help.add_command(label='Tsutsujiについて...', command=self.aboutwindow)
        
        self.master['menu'] = self.menubar
    def bind_keyevent(self):
        self.master.bind("<Control-o>", self.opencfg)
        self.master.bind("<Control-m>", self.measure)
        self.master.bind("<Control-g>", self.generate_output)
        self.master.bind("<Control-t>", self.staticmapctrl.create_paramwindow)
        self.master.bind("<Shift-Return>", self.getmaptile)
        self.master.bind("<F5>", self.reloadcfg)
        self.master.bind("<Alt-F4>", self.ask_quit)
        self.master.bind("<Return>", self.press_return)
        self.master.bind("<Shift-Left>", self.press_arrowkey)
        self.master.bind("<Shift-Right>", self.press_arrowkey)
        self.master.bind("<Shift-Up>", self.press_arrowkey)
        self.master.bind("<Shift-Down>", self.press_arrowkey)
    def ask_quit(self, event=None, ask=True):
        if ask:
            if tk.messagebox.askyesno(message='Tsutsuji を終了しますか？'):
                self.quit()
        else:
            self.quit()
    def opencfg(self, event=None, in_dir=None):
        inputdir = filedialog.askopenfilename() if in_dir == None else in_dir
        print('loading',inputdir)
        self.trackcontrol.loadcfg(inputdir)
        self.trackcontrol.loadmap()
        if self.trackcontrol.conf.general['backimg'] is not None:
            self.backimgctrl.load_setting(path = self.trackcontrol.conf.general['backimg'])
        elif self.backimgctrl.conf_path is not None:
            self.backimgctrl.load_setting(path = self.backimgctrl.conf_path)
        self.trackwindow.reset_treevalue()
        self.measurewindow.reload_trackkeys()

        plotsize = self.fig_plane.get_size_inches()
        self.staticmapctrl.setparams_fromcfg(self.trackcontrol.conf.maptile)
        self.staticmapctrl.getimg(self.viewp_scale_v.get(),plotsize[1]/plotsize[0])
        
        self.drawall()
    def reloadcfg(self, event=None):
        if self.trackcontrol.path is not None:
            self.opencfg(event=event,in_dir=self.trackcontrol.path)
    def draw2dplot(self):
        self.ax_plane.cla()
        self.trackcontrol.plot2d(self.ax_plane)
        self.fig_canvas.draw()
    def drawall(self):
        self.ax_plane.cla()
        self.trackcontrol.plot2d(self.ax_plane)
        for key in self.plot_marker_ctrl.keys():
            if self.plot_marker_ctrl[key]['variable'].get():
                self.trackcontrol.plot_symbols(self.ax_plane,key)

        self.measurewindow.drawall()
        plotsize = self.fig_plane.get_size_inches()
        
        if self.view_whole_v.get() == 'True':
            imgarea = self.backimgctrl.imgsarea()
            imgarea = self.trackcontrol.drawarea(imgarea)
            
            self.ax_plane.set_xlim(imgarea[0],imgarea[1])
            self.ax_plane.set_ylim(imgarea[2],imgarea[3])
        else:
            center = [self.viewpos_v[0].get(),self.viewpos_v[1].get()]
            windowratio = 1/self.aspectratio_v.get()*plotsize[1]/plotsize[0] # 平面図のアスペクト比を取得
            scalex = self.viewp_scale_v.get()
            scaley = windowratio * scalex
            
            self.ax_plane.set_xlim(center[0]-scalex/2, center[0]+scalex/2)
            self.ax_plane.set_ylim(center[1]-scaley/2, center[1]+scaley/2)
    
        self.staticmapctrl.showimg(self.ax_plane,as_ratio=plotsize[1]/plotsize[0],ymag=self.aspectratio_v.get())

        for i in self.backimgctrl.imgs.keys():
            self.backimgctrl.imgs[i].show(self.ax_plane,as_ratio=plotsize[1]/plotsize[0],ymag=self.aspectratio_v.get())

        self.ax_plane.invert_yaxis()
        self.fig_canvas.draw()
    def move_xy(self,x,y):
        nowpos = [self.viewpos_v[0].get(),self.viewpos_v[1].get()]
        plotsize = self.fig_plane.get_size_inches()
        windowratio = 1/self.aspectratio_v.get()*plotsize[1]/plotsize[0]
        scalex = self.viewp_scale_v.get()
        scaley = windowratio * scalex

        self.viewpos_v[0].set(nowpos[0] + x*scalex/5)
        self.viewpos_v[1].set(nowpos[1] + y*scaley/5)
        self.drawall()
    def measure(self, event=None):
        self.measurewindow.create_widgets()
    def draw_tracks_cp(self):
        self.trackcontrol.plot_controlpoints(self.ax_plane)
        self.fig_canvas.draw()
    def generate_output(self, event=None):
        self.trackcontrol.generate_mapdata()
        self.get_othertrack()
    def aboutwindow(self, event=None):
        msg  = 'Tsutsuji trackcomputer\n'
        msg += 'Version '+__version__+'\n\n'
        msg += 'Copyright © 2023 konawasabi\n'
        msg += 'Released under the Apache License, Version 2.0 .\n'
        msg += 'https://www.apache.org/licenses/LICENSE-2.0'
        tk.messagebox.showinfo(message=msg)
    def open_webdocument(self, event=None):
        webbrowser.open('https://konawasabi.github.io/tsutsuji-trackcomputer/')
    def sendtopmost(self,event=None):
        self.master.lift()
        self.master.focus_force()
    def get_othertrack(self, event=None):
        self.trackcontrol.generate_otdata()
        self.trackwindow.reset_treevalue()
        self.drawall()
    def press_return(self, event=None):
        self.drawall()
        self.master.focus_force()
    def press_arrowkey(self, event=None):
        if event.keysym == 'Left':
            self.move_xy(-1,0)
        elif event.keysym == 'Right':
            self.move_xy(1,0)
        elif event.keysym == 'Up':
            self.move_xy(0,-1)
        elif event.keysym == 'Down':
            self.move_xy(0,1)
    def getmaptile(self, event=None):
        plotsize = self.fig_plane.get_size_inches()
        self.staticmapctrl.getimg(self.viewp_scale_v.get(),plotsize[1]/plotsize[0])
        self.drawall()
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
        sys.excepthook = info
        print('Debug mode')

    argparser = argparse.ArgumentParser()
    argparser.add_argument('filepath', metavar='F', type=str, help='input cfg file', nargs='?')
    argparser.add_argument('-n', '--nogui', help='no gui mode', action='store_true')
    args = argparser.parse_args()

    if args.nogui:
        if __debug__:
            def errorcatcher(type, value, tb):
                #print(type, value, tb,file=sys.stderr)
                print(value, file=sys.stderr)
                exit
            sys.excepthook = errorcatcher
        if args.filepath is None:
            raise Exception('no cfg file')
        trackcontrol = track_control.TrackControl()
        trackcontrol.loadcfg(args.filepath)
        trackcontrol.loadmap()
        trackcontrol.generate_mapdata()
    else:
        tk.CallWrapper = Catcher
        root = tk.Tk()
        app = mainwindow(master=root)
        #if len(sys.argv)>1:
        #    app.opencfg(in_dir=sys.argv[1])
        if args.filepath is not None:
            app.opencfg(in_dir=args.filepath)
        app.mainloop()
