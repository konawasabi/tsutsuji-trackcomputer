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
import staticmap
import io
import requests

from kobushi import dialog_multifields
from tsutsuji import math

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

class StaticMapControl():
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow


        self.toshow = False
        #width  = self.output_data.shape[1]
        #height = self.output_data.shape[0]
        self.origin = [0,0]
        self.shift = [0,0]
        self.rotrad = 0
        self.alpha = 0.8
        self.extent = [-900/2,900/2,-700/2,700/2]
        self.scale = 1

        self.map = None
        self.img = None
        self.origin_longlat = [139.7413, 35.6580] #longitude: 経度[deg]、latitude: 緯度[deg]
        self.template_url = 'https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png'#'https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/{z}/{x}/{y}.jpg'
        self.set_baseurl(self.template_url)
        
    def set_baseurl(self, url):
        self.map = None
        self.map = staticmap.StaticMap(800, 600, url_template=url)
        self.map.request_timeout = 10
    def canvas_size(self):
        print(self.mainwindow.ax_plane.get_position())
        print(self.mainwindow.ax_plane.figure.get_size_inches())
    def setparamdialog(self):
        inputvals = dialog_multifields.dialog_multifields(self.mainwindow,\
                                                          [{'name':'origin_longitude', 'type':'Double', 'label':'原点 東経', 'default':self.origin_longlat[0]},\
                                                           {'name':'origin_latitude', 'type':'Double', 'label':'原点 北緯', 'default':self.origin_longlat[1]},\
                                                           {'name':'template_url', 'type':'str', 'label':'template URL', 'default':self.template_url}])
        if inputvals.result == 'OK':
            for i in inputvals.variables.keys():
                print(i, inputvals.variables[i].get())
            self.origin_longlat = [inputvals.variables['origin_longitude'].get(), inputvals.variables['origin_latitude'].get()]
            self.template_url = inputvals.variables['template_url'].get()
            self.set_baseurl(self.template_url)
            if False:
                import pdb
                pdb.set_trace()
    def getimg(self):
        if False:
            import pdb
            pdb.set_trace()
        self.img = None
        self.img = self.map.render(zoom=16, center=self.origin_longlat)
        self.toshow = True
        print(self.img)
    def showimg(self,ax,as_ratio=1,ymag=1):
        if self.toshow:
            #self.rotate(self.rotrad)
            #as_ratio_mod = (self.extent[1]-self.extent[0])/(self.extent[3]-self.extent[2])*as_ratio
            ax.imshow(self.img,alpha=self.alpha,extent=[self.extent[0],self.extent[1],self.extent[3],self.extent[2]],aspect=ymag)

class TileMapControl():
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow


        self.toshow = False
        #width  = self.output_data.shape[1]
        #height = self.output_data.shape[0]
        self.origin = [0,0]
        self.shift = [0,0]
        self.rotrad = 0
        self.alpha = 0.8
        self.extent = [-900/2,900/2,-700/2,700/2]
        self.scale = 1

        self.map = None
        self.img = None
        self.origin_longlat = [139.7413, 35.6580] #longitude: 経度[deg]、latitude: 緯度[deg]
        self.position = [0, 0]
        self.zoom = 15
        self.template_url = 'https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png'#'https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/{z}/{x}/{y}.jpg'
        
    def set_baseurl(self, url):
        pass
    def canvas_size(self):
        print(self.mainwindow.ax_plane.get_position())
        print(self.mainwindow.ax_plane.figure.get_size_inches())
    def setparamdialog(self):
        inputvals = dialog_multifields.dialog_multifields(self.mainwindow,\
                                                          [{'name':'origin_longitude', 'type':'Double', 'label':'原点 東経', 'default':self.origin_longlat[0]},\
                                                           {'name':'origin_latitude', 'type':'Double', 'label':'原点 北緯', 'default':self.origin_longlat[1]},\
                                                           {'name':'pos_x', 'type':'Double', 'label':'中心座標x', 'default':self.position[0]},\
                                                           {'name':'pos_y', 'type':'Double', 'label':'中心座標y', 'default':self.position[1]},\
                                                           {'name':'zoom', 'type':'Integer', 'label':'原点 北緯', 'default':self.zoom},\
                                                           {'name':'template_url', 'type':'str', 'label':'template URL', 'default':self.template_url}])
        if inputvals.result == 'OK':
            for i in inputvals.variables.keys():
                print(i, inputvals.variables[i].get())
            self.origin_longlat = [inputvals.variables['origin_longitude'].get(), inputvals.variables['origin_latitude'].get()]
            self.position = [inputvals.variables['pos_x'].get(), inputvals.variables['pos_y'].get()]
            self.zoom = int(inputvals.variables['zoom'].get())
            self.template_url = inputvals.variables['template_url'].get()
    def getimg(self):
        if False:
            import pdb
            pdb.set_trace()
        self.img = None
        
        if '{z}' not in self.template_url or '{x}' not in self.template_url or '{y}' not in self.template_url:
            raise Exception('Invalid template_url')
        else:
            url_base = self.template_url.replace('{z}', '{:d}').replace('{x}', '{:d}').replace('{y}', '{:d}')

        width = 900
        height = 700
        zoom = self.zoom

        origin = self.origin_longlat
        canvas_center = [self.mainwindow.viewpos_v[0].get(), self.mainwindow.viewpos_v[1].get()]
        
        border_lu = math.calc_xy2pl(-(-height/2 + canvas_center[1]), (-width/2 + canvas_center[0]), origin[1], origin[0])
        border_rd = math.calc_xy2pl(-(height/2 + canvas_center[1]), (width/2 + canvas_center[0]), origin[1], origin[0])

        px_lu = [math.long2px(border_lu[1],zoom), math.lat2py(border_lu[0],zoom)]
        tile_lu =[int(px_lu[0]/256), int(px_lu[1]/256)]
        rel_lu = [px_lu[0]%256, px_lu[1]%256]

        px_rd = [math.long2px(border_rd[1],zoom), math.lat2py(border_rd[0],zoom)]
        tile_rd =[int(px_rd[0]/256), int(px_rd[1]/256)]
        rel_rd = [px_rd[0]%256, px_rd[1]%256]

        x_min = tile_lu[0]
        x_max = tile_rd[0]
        y_min = tile_lu[1]
        y_max = tile_rd[1]

        pos_tile_corner = {}
        pos_tile_corner['lu'] = math.calc_pl2xy(math.py2lat(tile_lu[1]*256, zoom), math.px2long((tile_lu[0])*256, zoom), origin[1],origin[0])
        pos_tile_corner['rd'] = math.calc_pl2xy(math.py2lat((tile_rd[1]+1)*256, zoom), math.px2long((tile_rd[0]+1)*256, zoom), origin[1],origin[0])

        extent = [pos_tile_corner['lu'][1],\
                  pos_tile_corner['rd'][1], \
                  -pos_tile_corner['lu'][0],\
                  -pos_tile_corner['rd'][0]]

        x_num = x_max-x_min +1
        y_num = y_max-y_min +1

        result = Image.new('RGB', (256*x_num, 256*y_num), (0,0,0))
        for i in range(0,x_num):
            for j in range(0,y_num):
                url_toget = url_base.format(zoom,x_min+i,y_min+j)
                print(url_toget)

                # core
                img_piece = Image.open(io.BytesIO(requests.get(url_toget).content))

                result.paste(img_piece, (256*i, 256*j))

        #print(extent, border_lu, border_rd)

        print('Done')
        self.img = result
        self.extent = extent
        self.toshow = True
    def showimg(self,ax,as_ratio=1,ymag=1):
        if self.toshow:
            #self.rotate(self.rotrad)
            #as_ratio_mod = (self.extent[1]-self.extent[0])/(self.extent[3]-self.extent[2])*as_ratio
            ax.imshow(self.img,alpha=self.alpha,extent=[self.extent[0],self.extent[1],self.extent[3],self.extent[2]],aspect=ymag)
