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

class BackImgControl_Height():
    class BackImgData():
        def __init__(self,path):
            self.path = path
            self.img = Image.open(path)
            self.output_data = np.array(self.img)
            self.toshow = True
            width  = self.output_data.shape[1]
            height = self.output_data.shape[0]
            self.width = width
            self.height = height
            self.origin = [0,0]
            self.shift = [0,0]
            self.rotrad = 0
            self.alpha = 1.0
            self.extent = [0,width,0,height]
            self.scale = 1

            self.pos_img0 = [0,0]
            self.pos_img1 = [width,height]
            self.pos_plot0 = [0,0]
            self.pos_plot1 = [width, height]
        def rotate(self,rad):
            pass
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
        def reshape(self):
            trans_f = [lambda x: (self.pos_plot1[0] - self.pos_plot0[0])/(self.pos_img1[0]-self.pos_img0[0])*(x - self.pos_img0[0]) + self.pos_plot0[0],\
                       lambda y: (self.pos_plot1[1] - self.pos_plot0[1])/(self.pos_img1[1]-self.pos_img0[1])*(y - self.pos_img0[1]) + self.pos_plot0[1]]

            self.extent = [trans_f[0](0), \
                           trans_f[0](self.width), \
                           trans_f[1](self.height),\
                           trans_f[1](0),]
            #print(self.extent)
        def show(self,ax,as_ratio=1,ymag=1):
            if self.toshow:
                self.reshape()
                #self.rotate(self.rotrad)
                #as_ratio_mod = (self.extent[1]-self.extent[0])/(self.extent[3]-self.extent[2])*as_ratio
                ax.imshow(self.output_data,alpha=self.alpha,extent=[self.extent[0],self.extent[1],self.extent[3],self.extent[2]],aspect='auto')#,aspect=ymag)
    def __init__(self,mainwindow):
        self.mainwindow = mainwindow
        self.imgs = {}
        self.conf_path = None
        self.master = None
    def create_window(self):
        if self.master == None:
            self.master = tk.Toplevel(self.mainwindow.master)
            self.mainframe = ttk.Frame(self.master, padding='3 3 3 3')
            self.mainframe.columnconfigure(0, weight=1)
            self.mainframe.rowconfigure(0, weight=1)
            self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

            self.master.title('Background images (Height)')
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

            self.x0_l = ttk.Label(self.input_frame, text='x0')
            self.x1_l = ttk.Label(self.input_frame, text='x1')
            self.y0_l = ttk.Label(self.input_frame, text='y0')
            self.y1_l = ttk.Label(self.input_frame, text='y1')
            
            #self.rot_l = ttk.Label(self.input_frame, text='rotation')
            self.alpha_l = ttk.Label(self.input_frame, text='alpha')
            
            self.d0_l = ttk.Label(self.input_frame, text='dist0')
            self.d1_l = ttk.Label(self.input_frame, text='dist1')
            self.h0_l = ttk.Label(self.input_frame, text='h0')
            self.h1_l = ttk.Label(self.input_frame, text='h1')
            #self.scale_l = ttk.Label(self.input_frame, text='scale')

            self.x0_l.grid(column=0, row=0, sticky=(tk.E,tk.W))
            self.y0_l.grid(column=2, row=0, sticky=(tk.E,tk.W))
            self.x1_l.grid(column=0, row=1, sticky=(tk.E,tk.W))
            self.y1_l.grid(column=2, row=1, sticky=(tk.E,tk.W))
            
            #self.rot_l.grid(column=0, row=4, sticky=(tk.E,tk.W))
            self.alpha_l.grid(column=2, row=4, sticky=(tk.E,tk.W))
            
            self.d0_l.grid(column=0, row=2, sticky=(tk.E,tk.W))
            self.h0_l.grid(column=2, row=2, sticky=(tk.E,tk.W))
            self.d1_l.grid(column=0, row=3, sticky=(tk.E,tk.W))
            self.h1_l.grid(column=2, row=3, sticky=(tk.E,tk.W))
            #self.scale_l.grid(column=0, row=5, sticky=(tk.E,tk.W))

            #self.extent = [tk.DoubleVar(value=0),tk.DoubleVar(value=0),tk.DoubleVar(value=0),tk.DoubleVar(value=0)]
            self.pos_img0 = [tk.DoubleVar(value=0),tk.DoubleVar(value=0)]
            self.pos_img1 = [tk.DoubleVar(value=0),tk.DoubleVar(value=0)]
            self.pos_plot0 = [tk.DoubleVar(value=0),tk.DoubleVar(value=0)]
            self.pos_plot1 = [tk.DoubleVar(value=0),tk.DoubleVar(value=0)]
            self.rot_v = tk.DoubleVar(value=0)
            self.alpha_v = tk.DoubleVar(value=0)
            self.toshow_v = tk.BooleanVar(value=False)
            self.origin = [tk.DoubleVar(value=0),tk.DoubleVar(value=0)]
            self.shift = [tk.DoubleVar(value=0),tk.DoubleVar(value=0)]
            self.scale_v = tk.DoubleVar(value=1)

            
            self.x0_e = ttk.Entry(self.input_frame, textvariable=self.pos_img0[0],width=5)
            self.y0_e = ttk.Entry(self.input_frame, textvariable=self.pos_img0[1],width=5)
            self.x1_e = ttk.Entry(self.input_frame, textvariable=self.pos_img1[0],width=5)
            self.y1_e = ttk.Entry(self.input_frame, textvariable=self.pos_img1[1],width=5)
            
            
            self.d0_e = ttk.Entry(self.input_frame, textvariable=self.pos_plot0[0],width=5)
            self.h0_e = ttk.Entry(self.input_frame, textvariable=self.pos_plot0[1],width=5)
            self.d1_e = ttk.Entry(self.input_frame, textvariable=self.pos_plot1[0],width=5)
            self.h1_e = ttk.Entry(self.input_frame, textvariable=self.pos_plot1[1],width=5)
            
            #self.rot_e = ttk.Entry(self.input_frame, textvariable=self.rot_v,width=5)
            self.alpha_e = ttk.Entry(self.input_frame, textvariable=self.alpha_v,width=5)
            #self.scale_e = ttk.Entry(self.input_frame, textvariable=self.scale_v,width=5)
            self.show_chk = ttk.Checkbutton(self.input_frame, text='Show', variable=self.toshow_v)

            
            self.x0_e.grid(column=1, row=0, sticky=(tk.E,tk.W))
            self.y0_e.grid(column=3, row=0, sticky=(tk.E,tk.W))
            self.x1_e.grid(column=1, row=1, sticky=(tk.E,tk.W))
            self.y1_e.grid(column=3, row=1, sticky=(tk.E,tk.W))
            
            #self.rot_e.grid(column=1, row=4, sticky=(tk.E,tk.W))
            self.alpha_e.grid(column=3, row=4, sticky=(tk.E,tk.W))
            self.show_chk.grid(column=3, row=5, sticky=(tk.E,tk.W))
            
            self.d0_e.grid(column=1, row=2, sticky=(tk.E,tk.W))
            self.h0_e.grid(column=3, row=2, sticky=(tk.E,tk.W))
            self.d1_e.grid(column=1, row=3, sticky=(tk.E,tk.W))
            self.h1_e.grid(column=3, row=3, sticky=(tk.E,tk.W))
            #self.scale_e.grid(column=1, row=5, sticky=(tk.E,tk.W))
            

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

            '''
            self.button_save = ttk.Button(self.button_frame, text="Save", command=self.save_setting)
            self.button_save.grid(column=0, row=1, sticky=(tk.E,tk.S))
            self.button_load = ttk.Button(self.button_frame, text="Load", command=self.load_setting)
            self.button_load.grid(column=1, row=1, sticky=(tk.E,tk.S))
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
        '''
        for i in [0,1,2,3]:
            tmp = self.extent[i].get()
            print(tmp)
            self.imgs[selected].extent[i] = float(tmp)
        '''
        for i in [0,1]:
            self.imgs[selected].pos_img0[i]=float(self.pos_img0[i].get())
            self.imgs[selected].pos_img1[i]=float(self.pos_img1[i].get())
            self.imgs[selected].pos_plot0[i]=float(self.pos_plot0[i].get())
            self.imgs[selected].pos_plot1[i]=float(self.pos_plot1[i].get())
            
        self.imgs[selected].alpha = self.alpha_v.get()
        self.imgs[selected].toshow = self.toshow_v.get()
        '''
        self.imgs[selected].scale = self.scale_v.get()
        
        for i in [0,1]:
            self.imgs[selected].origin[i] = self.origin[i].get()
            self.imgs[selected].shift[i] = self.shift[i].get()
        '''

        '''
        if self.rot_v.get() != self.imgs[selected].rotrad:
            self.imgs[selected].rotrad = self.rot_v.get()
            #self.imgs[selected].rotate(self.imgs[selected].rotrad)
        '''
        self.mainwindow.drawall()
    def clickimglist(self,event):
        if len(self.imglist_sb.selection())>0:
            selected = str(self.imglist_sb.selection()[0])
            #print('Hi',event,selected)
            for i in [0,1]:
                self.pos_img0[i].set(self.imgs[selected].pos_img0[i])
                self.pos_img1[i].set(self.imgs[selected].pos_img1[i])
                self.pos_plot0[i].set(self.imgs[selected].pos_plot0[i])
                self.pos_plot1[i].set(self.imgs[selected].pos_plot1[i])
            #self.rot_v.set(self.imgs[selected].rotrad)
            self.alpha_v.set(self.imgs[selected].alpha)
            self.toshow_v.set(self.imgs[selected].toshow)
            '''
            self.scale_v.set(self.imgs[selected].scale)
            for i in [0,1]:
                self.origin[i].set(self.imgs[selected].origin[i])
                self.shift[i].set(self.imgs[selected].shift[i])
            '''
            
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
                #fp.writelines('rot = {:f}\n'.format(self.imgs[imgkey].rotrad))
                fp.writelines('alpha = {:f}\n'.format(self.imgs[imgkey].alpha))
                #fp.writelines('scale = {:f}\n'.format(self.imgs[imgkey].scale))
                #fp.writelines('origin = {:f},{:f}\n'.format(self.imgs[imgkey].origin[0],self.imgs[imgkey].origin[1]))
                #fp.writelines('shift = {:f},{:f}\n'.format(self.imgs[imgkey].shift[0],self.imgs[imgkey].shift[1]))
                fp.writelines('pos_img0 = {:f},{:f}\n'.format(self.imgs[imgkey].pos_img0[0],self.imgs[imgkey].pos_img0[1]))
                fp.writelines('pos_img1 = {:f},{:f}\n'.format(self.imgs[imgkey].pos_img1[0],self.imgs[imgkey].pos_img1[1]))
                fp.writelines('pos_plot0 = {:f},{:f}\n'.format(self.imgs[imgkey].pos_plot0[0],self.imgs[imgkey].pos_plot0[1]))
                fp.writelines('pos_plot1 = {:f},{:f}\n'.format(self.imgs[imgkey].pos_plot1[0],self.imgs[imgkey].pos_plot1[1]))
                
                fp.writelines('\n')
            fp.close()
    def load_setting(self,path=None):
        if path is None:
            path = filedialog.askopenfilename()
            for key in self.imglist_sb.get_children():
                self.imglist_sb.delete(key)
        conf = configparser.ConfigParser()
        conf.read(path)
        self.conf_path = path

        
        self.imgs = {}
        for sections in conf.sections():
            self.imgs[sections]=self.BackImgData(sections)
            tmp = conf[sections]['pos_img0'].split(',')
            self.imgs[sections].pos_img0[0] = float(tmp[0])
            self.imgs[sections].pos_img0[1] = float(tmp[1])
            tmp = conf[sections]['pos_img1'].split(',')
            self.imgs[sections].pos_img1[0] = float(tmp[0])
            self.imgs[sections].pos_img1[1] = float(tmp[1])
            tmp = conf[sections]['pos_plot0'].split(',')
            self.imgs[sections].pos_plot0[0] = float(tmp[0])
            self.imgs[sections].pos_plot0[1] = float(tmp[1])
            tmp = conf[sections]['pos_plot1'].split(',')
            self.imgs[sections].pos_plot1[0] = float(tmp[0])
            self.imgs[sections].pos_plot1[1] = float(tmp[1])

            #self.imgs[sections].rotrad = float(conf[sections]['rot'])
            self.imgs[sections].alpha = float(conf[sections]['alpha'])
            #self.imgs[sections].scale = float(conf[sections]['scale'])

            if path is None:
                self.imglist_sb.insert('',tk.END, sections, text=sections)
                self.imglist_sb.selection_set(sections)
        self.mainwindow.drawall()
    def sendtopmost(self,event=None):
        self.master.lift()
        self.master.focus_force()
    def closewindow(self):
        self.master.withdraw()
        self.master = None
