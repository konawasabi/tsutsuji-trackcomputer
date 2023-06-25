#
#    Copyright 2021-2022 konawasabi
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

import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as filedialog
import tkinter.simpledialog as simpledialog

import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import io
import requests

from kobushi import dialog_multifields
from . import math

import configparser

class BackImgControl():
    class BackImgData():
        def __init__(self,path):
            self.path = path
            self.img = Image.open(path)
            self.output_data = np.array(self.img)
            self.toshow = True
            width  = self.output_data.shape[1]
            height = self.output_data.shape[0]
            self.origin = [0,0]
            self.shift = [0,0]
            self.rotrad = 0
            self.alpha = 0.5
            self.extent = [0,width,0,-height]
            self.scale = 1
        def rotate(self,rad):
            def rotmatrix(tau1):
                '''２次元回転行列を返す。
                tau1: 回転角度 [rad]
                '''
                return np.array([[np.cos(tau1), -np.sin(tau1)], [np.sin(tau1),  np.cos(tau1)]])
            self.rotrad = rad
            self.output_data = np.array(self.img.rotate(-rad,expand=True))
            
            width  = np.array(self.img).shape[1]
            height = np.array(self.img).shape[0]
            
            shape_orig = np.vstack((0,0))
            shape_orig = np.hstack((shape_orig,np.vstack((width,0))))
            shape_orig = np.hstack((shape_orig,np.vstack((width,height))))
            shape_orig = np.hstack((shape_orig,np.vstack((0,height))))
            
            shape_rot = np.dot(rotmatrix(np.deg2rad(rad)),(shape_orig - np.vstack((self.origin[0],self.origin[1])))*self.scale)
            shape_rot = shape_rot + np.vstack((self.shift[0],self.shift[1]))
            
            self.extent = [min(shape_rot[0]),max(shape_rot[0]),min(shape_rot[1]),max(shape_rot[1])]
        def show(self,ax,as_ratio=1,ymag=1):
            if self.toshow:
                self.rotate(self.rotrad)
                #as_ratio_mod = (self.extent[1]-self.extent[0])/(self.extent[3]-self.extent[2])*as_ratio
                ax.imshow(self.output_data,alpha=self.alpha,extent=[self.extent[0],self.extent[1],self.extent[3],self.extent[2]],aspect=ymag)
    def __init__(self,mainwindow):
        self.mainwindow = mainwindow
        self.imgs = {}
        self.conf_path = None
        self.master = None
    def create_window(self):
        if self.master == None:
            self.master = tk.Toplevel(self.mainwindow)
            self.mainframe = ttk.Frame(self.master, padding='3 3 3 3')
            self.mainframe.columnconfigure(0, weight=1)
            self.mainframe.rowconfigure(0, weight=1)
            self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

            self.master.title('Background images')
            self.master.protocol('WM_DELETE_WINDOW', self.closewindow)

            #self.imglist_val_list = list(self.imgs.keys())
            #self.imglist_val = tk.StringVar(value=self.imglist_val_list)

            self.imglist_sb = ttk.Treeview(self.mainframe,selectmode='browse',height = 4)
            self.imglist_sb.column('#0',width=500)
            self.imglist_sb.heading('#0',text='Filepath')
            for i in list(self.imgs.keys()):
                self.imglist_sb.insert('',tk.END, i, text=i)
            self.imglist_sb.grid(column=0, row=0, sticky=(tk.S))
            self.imglist_sb.bind('<<TreeviewSelect>>', self.clickimglist)

            self.input_frame = ttk.Frame(self.mainframe, padding='3 3 3 3')
            self.input_frame.grid(column=0, row=1, sticky=(tk.E,tk.W))

            '''
            self.xmin_l = ttk.Label(self.input_frame, text='xmin')
            self.xmax_l = ttk.Label(self.input_frame, text='xmax')
            self.ymin_l = ttk.Label(self.input_frame, text='ymin')
            self.ymax_l = ttk.Label(self.input_frame, text='ymax')
            '''
            self.rot_l = ttk.Label(self.input_frame, text='rotation')
            self.alpha_l = ttk.Label(self.input_frame, text='alpha')
            self.xo_l = ttk.Label(self.input_frame, text='x0')
            self.yo_l = ttk.Label(self.input_frame, text='y0')
            self.xsh_l = ttk.Label(self.input_frame, text='xshift')
            self.ysh_l = ttk.Label(self.input_frame, text='yshift')
            self.scale_l = ttk.Label(self.input_frame, text='scale')

            '''
            self.xmin_l.grid(column=0, row=0, sticky=(tk.E,tk.W))
            self.xmax_l.grid(column=0, row=1, sticky=(tk.E,tk.W))
            self.ymin_l.grid(column=2, row=0, sticky=(tk.E,tk.W))
            self.ymax_l.grid(column=2, row=1, sticky=(tk.E,tk.W))
            '''
            self.rot_l.grid(column=0, row=4, sticky=(tk.E,tk.W))
            self.alpha_l.grid(column=2, row=4, sticky=(tk.E,tk.W))
            self.xo_l.grid(column=0, row=2, sticky=(tk.E,tk.W))
            self.yo_l.grid(column=2, row=2, sticky=(tk.E,tk.W))
            self.xsh_l.grid(column=0, row=3, sticky=(tk.E,tk.W))
            self.ysh_l.grid(column=2, row=3, sticky=(tk.E,tk.W))
            self.scale_l.grid(column=0, row=5, sticky=(tk.E,tk.W))

            self.extent = [tk.DoubleVar(value=0),tk.DoubleVar(value=0),tk.DoubleVar(value=0),tk.DoubleVar(value=0)]
            self.rot_v = tk.DoubleVar(value=0)
            self.alpha_v = tk.DoubleVar(value=0)
            self.toshow_v = tk.BooleanVar(value=False)
            self.origin = [tk.DoubleVar(value=0),tk.DoubleVar(value=0)]
            self.shift = [tk.DoubleVar(value=0),tk.DoubleVar(value=0)]
            self.scale_v = tk.DoubleVar(value=1)

            '''
            self.xmin_e = ttk.Entry(self.input_frame, textvariable=self.extent[0],width=5)
            self.xmax_e = ttk.Entry(self.input_frame, textvariable=self.extent[1],width=5)
            self.ymin_e = ttk.Entry(self.input_frame, textvariable=self.extent[2],width=5)
            self.ymax_e = ttk.Entry(self.input_frame, textvariable=self.extent[3],width=5)
            '''
            
            self.xo_e = ttk.Entry(self.input_frame, textvariable=self.origin[0],width=5)
            self.yo_e = ttk.Entry(self.input_frame, textvariable=self.origin[1],width=5)
            self.xsh_e = ttk.Entry(self.input_frame, textvariable=self.shift[0],width=5)
            self.ysh_e = ttk.Entry(self.input_frame, textvariable=self.shift[1],width=5)
            self.rot_e = ttk.Entry(self.input_frame, textvariable=self.rot_v,width=5)
            self.alpha_e = ttk.Entry(self.input_frame, textvariable=self.alpha_v,width=5)
            self.scale_e = ttk.Entry(self.input_frame, textvariable=self.scale_v,width=5)
            self.show_chk = ttk.Checkbutton(self.input_frame, text='Show', variable=self.toshow_v)

            '''
            self.xmin_e.grid(column=1, row=0, sticky=(tk.E,tk.W))
            self.xmax_e.grid(column=1, row=1, sticky=(tk.E,tk.W))
            self.ymin_e.grid(column=3, row=0, sticky=(tk.E,tk.W))
            self.ymax_e.grid(column=3, row=1, sticky=(tk.E,tk.W))
            '''
            self.rot_e.grid(column=1, row=4, sticky=(tk.E,tk.W))
            self.alpha_e.grid(column=3, row=4, sticky=(tk.E,tk.W))
            self.show_chk.grid(column=3, row=5, sticky=(tk.E,tk.W))
            self.xo_e.grid(column=1, row=2, sticky=(tk.E,tk.W))
            self.yo_e.grid(column=3, row=2, sticky=(tk.E,tk.W))
            self.xsh_e.grid(column=1, row=3, sticky=(tk.E,tk.W))
            self.ysh_e.grid(column=3, row=3, sticky=(tk.E,tk.W))
            self.scale_e.grid(column=1, row=5, sticky=(tk.E,tk.W))

            self.button_frame = ttk.Frame(self.mainframe, padding='3 3 3 3')
            self.button_frame.grid(column=0, row=2, sticky=(tk.E,tk.W))
            self.button_add = ttk.Button(self.button_frame, text="Add", command=self.newimg)
            self.button_add.grid(column=0, row=0, sticky=(tk.S))
            self.button_delete = ttk.Button(self.button_frame, text="Delete", command=self.deleteimg)
            self.button_delete.grid(column=1, row=0, sticky=(tk.S))
            self.button_show = ttk.Button(self.button_frame, text="Refresh", command=self.showimg)
            self.button_show.grid(column=2, row=0, sticky=(tk.S))
            '''
            self.button_close = ttk.Button(self.button_frame, text="Close", command=self.master.destroy)
            self.button_close.grid(column=0, row=1, sticky=(tk.S))
            '''

            self.master.focus_set()
        else:
            self.sendtopmost()
    def newimg(self):
        inputdir = filedialog.askopenfilename()
        if inputdir != '':
            self.imgs[inputdir] = self.BackImgData(inputdir)
            #self.imgs.show(self.ax)
            #self.imglist_val_list.append(inputdir)
            #self.imglist_val.set(self.imglist_val_list)
            self.imglist_sb.insert('',tk.END, inputdir, text=inputdir)
            self.imglist_sb.selection_set(inputdir)
            self.mainwindow.drawall()
    def deleteimg(self):
        selected = str(self.imglist_sb.selection()[0])
        del self.imgs[selected]
        self.imglist_sb.delete(selected)
        self.mainwindow.drawall()
    def showimg(self):

        selected = str(self.imglist_sb.selection()[0])
        for i in [0,1,2,3]:
            self.imgs[selected].extent[i] = self.extent[i].get()
        self.imgs[selected].alpha = self.alpha_v.get()
        self.imgs[selected].toshow = self.toshow_v.get()
        self.imgs[selected].scale = self.scale_v.get()
        for i in [0,1]:
            self.imgs[selected].origin[i] = self.origin[i].get()
            self.imgs[selected].shift[i] = self.shift[i].get()
            
        if self.rot_v.get() != self.imgs[selected].rotrad:
            self.imgs[selected].rotrad = self.rot_v.get()
            #self.imgs[selected].rotate(self.imgs[selected].rotrad)
        self.mainwindow.drawall()
    def clickimglist(self,event):
        if len(self.imglist_sb.selection())>0:
            selected = str(self.imglist_sb.selection()[0])
            #print('Hi',event,selected)
            for i in [0,1,2,3]:
                self.extent[i].set(self.imgs[selected].extent[i])
            self.rot_v.set(self.imgs[selected].rotrad)
            self.alpha_v.set(self.imgs[selected].alpha)
            self.toshow_v.set(self.imgs[selected].toshow)
            self.scale_v.set(self.imgs[selected].scale)
            for i in [0,1]:
                self.origin[i].set(self.imgs[selected].origin[i])
                self.shift[i].set(self.imgs[selected].shift[i])
    def imgsarea(self, extent_input = None):
        extent = [0,0,0,0] if extent_input == None else extent_input
        for key in list(self.imgs.keys()):
            img = self.imgs[key]
            extent[0] = img.extent[0] if img.extent[0] < extent[0] else extent[0]
            extent[1] = img.extent[1] if img.extent[1] > extent[1] else extent[1]
            extent[2] = img.extent[2] if img.extent[2] < extent[2] else extent[2]
            extent[3] = img.extent[3] if img.extent[3] > extent[3] else extent[3]
        return extent
    def save_setting(self,outputpath=None):
        if outputpath is None:
            outputpath = filedialog.asksaveasfilename()
        if outputpath != '':
            fp = open(outputpath, 'w')
            for imgkey in self.imgs.keys():
                fp.writelines('[{:s}]\n'.format(imgkey))
                #fp.writelines('file = {:s}\n'.format(imgkey))
                fp.writelines('rot = {:f}\n'.format(self.imgs[imgkey].rotrad))
                fp.writelines('alpha = {:f}\n'.format(self.imgs[imgkey].alpha))
                fp.writelines('scale = {:f}\n'.format(self.imgs[imgkey].scale))
                fp.writelines('origin = {:f},{:f}\n'.format(self.imgs[imgkey].origin[0],self.imgs[imgkey].origin[1]))
                fp.writelines('shift = {:f},{:f}\n'.format(self.imgs[imgkey].shift[0],self.imgs[imgkey].shift[1]))
                fp.writelines('\n')
            fp.close()
    def load_setting(self,path=None):
        if path is None:
            path = filedialog.askopenfilename()
        conf = configparser.ConfigParser()
        conf.read(path)
        self.conf_path = path

        self.imgs = {}
        for sections in conf.sections():
            self.imgs[sections]=self.BackImgData(sections)
            origin = conf[sections]['origin'].split(',')
            self.imgs[sections].origin[0] = float(origin[0])
            self.imgs[sections].origin[1] = float(origin[1])
            shift = conf[sections]['shift'].split(',')
            self.imgs[sections].shift[0] = float(shift[0])
            self.imgs[sections].shift[1] = float(shift[1])

            self.imgs[sections].rotrad = float(conf[sections]['rot'])
            self.imgs[sections].alpha = float(conf[sections]['alpha'])
            self.imgs[sections].scale = float(conf[sections]['scale'])
        self.mainwindow.drawall()
    def sendtopmost(self,event=None):
        self.master.lift()
        self.master.focus_force()
    def closewindow(self):
        self.master.withdraw()
        self.master = None

class TileMapControl():
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self.master = None

        self.toshow = False
        self.rotrad = 0
        self.alpha = 0.8
        self.extent = [-900/2,900/2,-700/2,700/2]
        self.scale = 1

        self.img = None
        self.origin_longlat = [139.741357472222222, 35.6580992222222222] # longitude: 経度[deg]、latitude: 緯度[deg]
        self.origin_metric = [0,0] # tsutsuji座標系でorigin_longlatが相当する座標
        self.zoom = 15
        self.template_url = ''
        self.autozoom = False
        self.filename = None

        self.img_cache = {}
    def create_paramwindow(self,event=None):
        if self.master is None:
            self.master = tk.Toplevel(self.mainwindow)
            self.mainframe = ttk.Frame(self.master, padding='3 3 3 3')
            self.mainframe.columnconfigure(0, weight=1)
            self.mainframe.rowconfigure(0, weight=1)
            self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

            self.master.title('MapTile Parameters')
            self.master.protocol('WM_DELETE_WINDOW', self.closewindow)
            self.master.focus_set()

            self.entryframe = ttk.Frame(self.mainframe, padding='3 3 3 3')
            self.entryframe.columnconfigure(1, weight=1)
            self.entryframe.rowconfigure(0, weight=1)
            self.entryframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

            self.wd_variable = {}
            self.wd_label = {}
            self.wd_entry = {}

            entry_row = 0
            for name in ['longitude [deg]', 'latitude [deg]', 'x0 [m]', 'y0 [m]', 'zoomlevel [0-18]', 'alpha [0-1]']:
                self.wd_variable[name] = tk.DoubleVar()
                self.wd_label[name] = ttk.Label(self.entryframe, text = name)
                self.wd_entry[name] = ttk.Entry(self.entryframe, textvariable = self.wd_variable[name], width=25)
                self.wd_label[name].grid(column=0, row=entry_row, sticky=(tk.N, tk.E, tk.S))
                self.wd_entry[name].grid(column=1, row=entry_row, sticky=(tk.N, tk.W, tk.S))
                entry_row +=1

            self.wd_variable['longitude [deg]'].set(self.origin_longlat[0])
            self.wd_variable['latitude [deg]'].set(self.origin_longlat[1])
            self.wd_variable['x0 [m]'].set(self.origin_metric[0])
            self.wd_variable['y0 [m]'].set(self.origin_metric[1])
            self.wd_variable['zoomlevel [0-18]'].set(self.zoom)
            self.wd_variable['alpha [0-1]'].set(self.alpha)

            name = 'template_url'
            self.wd_variable[name] = tk.StringVar(value=self.template_url)
            self.wd_label[name] = ttk.Label(self.entryframe, text = name)
            self.wd_entry[name] = ttk.Entry(self.entryframe, textvariable = self.wd_variable[name], width=50)
            self.wd_label[name].grid(column=0, row=entry_row, sticky=(tk.N, tk.E, tk.S))
            self.wd_entry[name].grid(column=1, row=entry_row, sticky=(tk.N, tk.W, tk.S))
            entry_row += 1
            
            # ---

            self.btnframe = ttk.Frame(self.mainframe, padding='3 3 3 3')
            self.btnframe.columnconfigure(0, weight=1)
            self.btnframe.columnconfigure(1, weight=1)
            self.btnframe.rowconfigure(0, weight=1)
            self.btnframe.grid(column=0, row=1, sticky=(tk.N, tk.W, tk.E, tk.S))

            self.wd_btn = {}
            
            name = 'toshow'
            self.wd_variable[name] = tk.BooleanVar(value=self.toshow)
            self.wd_btn[name] = ttk.Checkbutton(self.btnframe, text=name, variable=self.wd_variable[name])

            name = 'autozoom'
            self.wd_variable[name] = tk.BooleanVar(value=self.autozoom)
            self.wd_btn[name] = ttk.Checkbutton(self.btnframe, text=name, variable=self.wd_variable[name])
            
            name = 'OK'
            self.wd_btn[name] = ttk.Button(self.btnframe, text=name, command=self.getparameters)
            name = 'Cancel'
            self.wd_btn[name] = ttk.Button(self.btnframe, text=name, command=self.closewindow)

            btn_col = 0
            self.wd_btn['toshow'].grid(column=btn_col, row=0, sticky=(tk.N, tk.W, tk.S))
            btn_col += 1
            self.wd_btn['autozoom'].grid(column=btn_col, row=0, sticky=(tk.N, tk.W, tk.S))
            
            btn_col += 1
            for name in ['Cancel', 'OK']:
                self.wd_btn[name].grid(column=btn_col, row=0, sticky=(tk.N, tk.E, tk.S))
                btn_col+=1
        else:
            self.sendtopmost()
    def getparameters(self):
        '''
        for i in self.wd_variable.keys():
            print(i, self.wd_variable[i].get())
        '''
        self.origin_longlat = [self.wd_variable['longitude [deg]'].get(),\
                               self.wd_variable['latitude [deg]'].get()]
        self.origin_metric = [self.wd_variable['x0 [m]'].get(),\
                              self.wd_variable['y0 [m]'].get()]
        self.zoom = int(self.wd_variable['zoomlevel [0-18]'].get())
        self.alpha = self.wd_variable['alpha [0-1]'].get()
        self.template_url = self.wd_variable['template_url'].get()
        self.toshow = self.wd_variable['toshow'].get()
        self.autozoom = self.wd_variable['autozoom'].get()
        self.closewindow()
    def sendtopmost(self,event=None):
        self.master.lift()
        self.master.focus_force()
    def closewindow(self):
        self.master.withdraw()
        self.master = None
        self.mainwindow.sendtopmost()
    def getimg(self, scalex, as_ratio, maptilenumwarning=36):
        if False:
            import pdb
            pdb.set_trace()

        if not self.toshow:
            return

        if '{z}' not in self.template_url or \
           '{x}' not in self.template_url or \
           '{y}' not in self.template_url:
            raise Exception('Invalid template_url')
        else:
            url_base = self.template_url.replace('{z}', '{:d}').replace('{x}', '{:d}').replace('{y}', '{:d}')

        width = scalex
        height = scalex*as_ratio

        if self.autozoom:

            tilenumx = int(width/123)
            zoom = 18 - int(np.sqrt((tilenumx/2)))
            '''
            zoom = 18
            for count in range(1,18):
                tilenumx = int(width/(123*count))
                if tilenumx**2 <= 8:
                    zoom = 18-(count-1)
                    break
            '''
            if zoom > 18:
                zoom = 18
            if zoom < 0:
                zoom = 0
        else:
            zoom = self.zoom

        # 基準となる緯度経度をorigin_metricだけオフセット
        origin = math.calc_xy2pl(self.origin_metric[1],\
                                 -self.origin_metric[0],\
                                 self.origin_longlat[1],\
                                 self.origin_longlat[0])
        origin = [origin[1],origin[0]]

        canvas_center = [self.mainwindow.viewpos_v[0].get(),\
                         self.mainwindow.viewpos_v[1].get()]

        # プロット画面の左上(lu)、右下(rd)座標を求め、緯度経度に変換する
        border_lu = math.calc_xy2pl(-(-height/2 + canvas_center[1]),\
                                    (-width/2 + canvas_center[0]),\
                                    origin[1],\
                                    origin[0])
        border_rd = math.calc_xy2pl(-(height/2 + canvas_center[1]),\
                                    (width/2 + canvas_center[0]),\
                                    origin[1],\
                                    origin[0])

        # プロット画面の左上、右下を含むマップタイル座標を求める
        # (1)座標を緯度経度->ピクセル座標に変換、(2)タイル座標に変換、(3)タイル内での相対位置を求める
        px_lu = [math.long2px(border_lu[1],zoom), math.lat2py(border_lu[0],zoom)]
        tile_lu =[int(px_lu[0]/256), int(px_lu[1]/256)]
        rel_lu = [px_lu[0]%256, px_lu[1]%256]

        px_rd = [math.long2px(border_rd[1],zoom), math.lat2py(border_rd[0],zoom)]
        tile_rd =[int(px_rd[0]/256), int(px_rd[1]/256)]
        rel_rd = [px_rd[0]%256, px_rd[1]%256]

        # 右上、左下を含むタイルの端点座標をm単位で求める
        pos_tile_corner = {}
        pos_tile_corner['lu'] = math.calc_pl2xy(math.py2lat(tile_lu[1]*256, zoom),\
                                                math.px2long((tile_lu[0])*256, zoom),\
                                                origin[1],\
                                                origin[0])
        pos_tile_corner['rd'] = math.calc_pl2xy(math.py2lat((tile_rd[1]+1)*256, zoom),\
                                                math.px2long((tile_rd[0]+1)*256, zoom),\
                                                origin[1],\
                                                origin[0])

        # 取得するマップタイルの表示範囲
        extent = [pos_tile_corner['lu'][1],\
                  pos_tile_corner['rd'][1], \
                  -pos_tile_corner['lu'][0],\
                  -pos_tile_corner['rd'][0]]

        # マップタイルデータ取得
        x_min = tile_lu[0]
        x_max = tile_rd[0]
        y_min = tile_lu[1]
        y_max = tile_rd[1]

        x_num = x_max-x_min +1
        y_num = y_max-y_min +1

        imgnum = 0
        for i in range(0,x_num):
            for j in range(0,y_num):
                url_toget = url_base.format(zoom,x_min+i,y_min+j)

                if url_toget not in self.img_cache.keys():
                    imgnum +=1

        if imgnum > maptilenumwarning:
            if not tk.messagebox.askokcancel('get {:d} maptiles'.format(imgnum),'{:d} 枚のmaptileをダウンロードします。続行しますか？'.format(imgnum)):
                print('Cancelled')
                return
        
        self.img = None
        result = Image.new('RGB', (256*x_num, 256*y_num), (0,0,0))

        counts = 0
        for i in range(0,x_num):
            for j in range(0,y_num):
                url_toget = url_base.format(zoom,x_min+i,y_min+j)

                try:
                    if url_toget not in self.img_cache.keys():
                        self.img_cache[url_toget] = Image.open(io.BytesIO(requests.get(url_toget, timeout=(10.0,10.0)).content))
                        message = ''
                    else:
                        message = 'cached'
                    result.paste(self.img_cache[url_toget], (256*i, 256*j))
                except Exception as e:
                    message = 'ERROR' #e

                print('{:d}/{:d}'.format(counts+1,x_num*y_num),url_toget,message)
                counts +=1
        print('Done')

        self.img = result
        self.extent = extent
        self.filename = 'x{:d}y{:d}z{:d}'.format(x_min,y_min,zoom)
    def showimg(self,ax,as_ratio=1,ymag=1):
        if self.toshow and self.img is not None:
            ax.imshow(self.img,alpha=self.alpha,extent=[self.extent[0],self.extent[1],self.extent[3],self.extent[2]],aspect=ymag)
    def setparams_fromcfg(self, cfgd):
        if cfgd is not None:
            self.toshow = cfgd['toshow']
            self.alpha = cfgd['alpha']

            self.origin_longlat = [cfgd['longitude'], cfgd['latitude']] # longitude: 経度[deg]、latitude: 緯度[deg]
            self.origin_metric = [cfgd['x0'], cfgd['y0']] # tsutsuji座標系でorigin_longlatが相当する座標
            self.zoom = cfgd['zoomlevel']
            self.autozoom = cfgd['autozoom']
            self.template_url = cfgd['template_url']
    def export(self):
        if self.img is not None:
            filetype = self.template_url.split('.')[-1]
            outputpath = filedialog.asksaveasfilename(initialfile=self.filename+'.'+filetype)
            if outputpath !='':
                self.img.save(outputpath)
                
                fp = open(outputpath.split('.')[0]+'.cfg','w')
                fp.writelines('[{:s}]\n'.format(outputpath))
                fp.writelines('rot = {:f}\n'.format(self.rotrad))
                fp.writelines('alpha = {:f}\n'.format(self.alpha))
                fp.writelines('scale = {:f}\n'.format(abs((self.extent[1]-self.extent[0])/self.img.width)))
                fp.writelines('origin = {:f},{:f}\n'.format(0,0))
                fp.writelines('shift = {:f},{:f}\n'.format(self.extent[0],self.extent[2]))
                fp.writelines('\n')
                fp.close()
