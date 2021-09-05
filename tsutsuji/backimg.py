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
            self.shown = True
            self.origin = [0,0]
            self.rotrad = 0
            self.alpha = 1
        def rotate(self,rad):
            self.rotrad = rad
            self.output_data = np.array(self.img.rotate(np.rad2deg(rad),expand=True))
        def show(self,ax):
            if self.shown:
                width  = self.output_data.shape[1]
                height = self.output_data.shape[0]
                print(width,height)
                ax.imshow(self.output_data,alpha=self.alpha,extent=[0,width,-height,0])
    def __init__(self,mainwindow):
        self.mainwindow = mainwindow
        self.imgs = None
    def create_window(self):
        self.master = tk.Toplevel(self.mainwindow)
        self.mainframe = ttk.Frame(self.master, padding='3 3 3 3')
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)
        self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        self.master.title('Background images')
        
        self.imglist_val_list = []
        self.imglist_val = tk.StringVar(value=self.imglist_val_list)
        self.imglist_sb = tk.Listbox(self.mainframe,listvariable=self.imglist_val)
        self.imglist_sb.grid(column=0, row=0, sticky=(tk.S))
        
        self.button_load = ttk.Button(self.mainframe, text="Load", command=self.newimg)
        self.button_load.grid(column=0, row=1, sticky=(tk.S))
        self.button_close = ttk.Button(self.mainframe, text="Close", command=self.master.destroy)
        self.button_close.grid(column=1, row=1, sticky=(tk.S))
        
        self.master.focus_set()
    def newimg(self):
        self.inputdir = filedialog.askopenfilename()
        if self.inputdir != '':
            self.imgs = self.BackImgData(self.inputdir)
            #self.imgs.show(self.ax)
            self.imglist_val_list.append(self.inputdir)
            self.imglist_val.set(self.imglist_val_list)
    def rotate(self):
        angle = simpledialog.askfloat('rotate','rotate angle [rad]')
        self.imgs.rotate(angle)
        self.imgs.show(self.ax)
        
