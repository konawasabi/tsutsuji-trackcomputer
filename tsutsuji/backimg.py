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

import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as filedialog
import tkinter.simpledialog as simpledialog

import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

class BackImgControl():
    class BackImgData():
        def __init__(self,path):
            self.path = path
            self.img = Image.open(path)
            self.output_data = np.array(self.img)
            self.toshow = True
            self.origin = [0,0]
            self.rotrad = 0
            self.alpha = 0.5
            width  = self.output_data.shape[1]
            height = self.output_data.shape[0]
            self.extent = [0,width,0,-height]
        def rotate(self,rad):
            self.rotrad = rad
            self.output_data = np.array(self.img.rotate(np.rad2deg(rad),expand=True))
        def show(self,ax):
            if self.toshow:
                width  = self.output_data.shape[1]
                height = self.output_data.shape[0]
                print(width,height)
                ax.imshow(self.output_data,alpha=self.alpha,extent=self.extent)
    def __init__(self,mainwindow):
        self.mainwindow = mainwindow
        self.imgs = {}
    def create_window(self):
        self.master = tk.Toplevel(self.mainwindow)
        self.mainframe = ttk.Frame(self.master, padding='3 3 3 3')
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)
        self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        self.master.title('Background images')
        
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
        
        self.xmin_l = ttk.Label(self.input_frame, text='xmin')
        self.xmax_l = ttk.Label(self.input_frame, text='xmax')
        self.ymin_l = ttk.Label(self.input_frame, text='ymin')
        self.ymax_l = ttk.Label(self.input_frame, text='ymax')
        self.rot_l = ttk.Label(self.input_frame, text='rotation')
        self.alpha_l = ttk.Label(self.input_frame, text='alpha')
        
        self.xmin_l.grid(column=0, row=0, sticky=(tk.E,tk.W))
        self.xmax_l.grid(column=0, row=1, sticky=(tk.E,tk.W))
        self.ymin_l.grid(column=2, row=0, sticky=(tk.E,tk.W))
        self.ymax_l.grid(column=2, row=1, sticky=(tk.E,tk.W))
        self.rot_l.grid(column=0, row=2, sticky=(tk.E,tk.W))
        self.alpha_l.grid(column=2, row=2, sticky=(tk.E,tk.W))
        
        self.extent = [tk.DoubleVar(value=0),tk.DoubleVar(value=0),tk.DoubleVar(value=0),tk.DoubleVar(value=0)]
        self.rot_v = tk.DoubleVar(value=0)
        self.alpha_v = tk.DoubleVar(value=0)
        self.toshow_v = tk.BooleanVar(value=False)
        
        self.xmin_e = ttk.Entry(self.input_frame, textvariable=self.extent[0])
        self.xmax_e = ttk.Entry(self.input_frame, textvariable=self.extent[1])
        self.ymin_e = ttk.Entry(self.input_frame, textvariable=self.extent[2])
        self.ymax_e = ttk.Entry(self.input_frame, textvariable=self.extent[3])
        self.rot_e = ttk.Entry(self.input_frame, textvariable=self.rot_v)
        self.alpha_e = ttk.Entry(self.input_frame, textvariable=self.alpha_v)
        self.show_chk = ttk.Checkbutton(self.input_frame, text='Show', variable=self.toshow_v)
        
        self.xmin_e.grid(column=1, row=0, sticky=(tk.E,tk.W))
        self.xmax_e.grid(column=1, row=1, sticky=(tk.E,tk.W))
        self.ymin_e.grid(column=3, row=0, sticky=(tk.E,tk.W))
        self.ymax_e.grid(column=3, row=1, sticky=(tk.E,tk.W))
        self.rot_e.grid(column=1, row=2, sticky=(tk.E,tk.W))
        self.alpha_e.grid(column=3, row=2, sticky=(tk.E,tk.W))
        self.show_chk.grid(column=1, row=3, sticky=(tk.E,tk.W))
        
        self.button_frame = ttk.Frame(self.mainframe, padding='3 3 3 3')
        self.button_frame.grid(column=0, row=2, sticky=(tk.E,tk.W))
        self.button_load = ttk.Button(self.button_frame, text="Load", command=self.newimg)
        self.button_load.grid(column=0, row=0, sticky=(tk.S))
        self.button_show = ttk.Button(self.button_frame, text="Show", command=self.showimg)
        self.button_show.grid(column=1, row=0, sticky=(tk.S))
        self.button_close = ttk.Button(self.button_frame, text="Close", command=self.master.destroy)
        self.button_close.grid(column=0, row=1, sticky=(tk.S))
        
        self.master.focus_set()
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
    def rotate(self):
        angle = simpledialog.askfloat('rotate','rotate angle [rad]')
        self.imgs.rotate(angle)
        self.imgs.show(self.ax)
    def showimg(self):
        selected = str(self.imglist_sb.selection()[0])
        for i in [0,1,2,3]:
            self.imgs[selected].extent[i] = self.extent[i].get()
        self.imgs[selected].alpha = self.alpha_v.get()
        self.imgs[selected].toshow = self.toshow_v.get()
        self.mainwindow.drawall()
    def clickimglist(self,event):
        selected = str(self.imglist_sb.selection()[0])
        #print('Hi',event,selected)
        for i in [0,1,2,3]:
            self.extent[i].set(self.imgs[selected].extent[i])
        self.rot_v.set(self.imgs[selected].rotrad)
        self.alpha_v.set(self.imgs[selected].alpha)
        self.toshow_v.set(self.imgs[selected].toshow)
