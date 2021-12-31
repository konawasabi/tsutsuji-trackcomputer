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

import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import ttk

from kobushi import trackcoordinate

from . import drawcursor
from . import solver


class measure():
    def __init__(self):
        pass
        
class trackplot():
    def __init__(self):
        self.curvegen = trackcoordinate.curve()
        self.result=np.array([[0,0]])
    def generate(self,A,phiA,phiB,Radius,lenTC1,lenTC2,tranfunc):
        delta_phi = phiB - phiA #曲線前後での方位変化
        
        if(lenTC1>0):
            tc1_tmp = self.curvegen.transition_curve(lenTC1,\
                                          0,\
                                          Radius,\
                                          0,\
                                          tranfunc) # 入口側の緩和曲線
        else:
            tc1_tmp=(np.array([[0,0]]),0,0)
            
        if(lenTC2>0):
            tc2_tmp = self.curvegen.transition_curve(lenTC2,\
                                          Radius,\
                                          0,\
                                          0,\
                                          tranfunc) # 出口側の緩和曲線
        else:
            tc2_tmp=(np.array([[0,0]]),0,0)

        phi_circular = delta_phi - tc1_tmp[1] - tc2_tmp[1] # 円軌道での方位角変化
        
        cc_tmp = self.curvegen.circular_curve(Radius*phi_circular,\
                                   Radius,\
                                   tc1_tmp[1]) # 円軌道

        phi_tc2 = tc1_tmp[1] + cc_tmp[1] # 出口側緩和曲線始端の方位角
        
        # A!=(0,0)が反映されない。必ずA=(0,0)として計算される。いろいろおかしいので要検証
        self.result = tc1_tmp[0]
        self.result = np.vstack((self.result,self.result[-1] + cc_tmp[0]))
        self.result = np.vstack((self.result,self.result[-1] + np.dot(self.curvegen.rotate(phi_tc2), tc2_tmp[0].T).T))
        
        self.result = np.dot(self.curvegen.rotate(phiA), self.result.T).T
        self.result += A


class interface():
    class unit():
        def __init__(self,name,parentwindow,frame,parent,row,color):
            self.pframe = frame
            self.parentwindow = parentwindow
            self.parent = parent
            self.name = name
            self.marker = drawcursor.marker(self,color=color)
            self.arrow = drawcursor.arrow(self)
            
            self.create_widgets(row)
        def create_widgets(self,row):
            self.name_l = ttk.Label(self.pframe, text=self.name)
            self.name_l.grid(column=0, row=row, sticky=(tk.E,tk.W))
            
            self.values = [tk.DoubleVar(value=0),tk.DoubleVar(value=0),tk.DoubleVar(value=0),tk.StringVar(value='')]
            self.x_e = ttk.Entry(self.pframe, textvariable=self.values[0],width=5)
            self.y_e = ttk.Entry(self.pframe, textvariable=self.values[1],width=5)
            self.theta_e = ttk.Entry(self.pframe, textvariable=self.values[2],width=5)
            self.track_e = ttk.Combobox(self.pframe, textvariable=self.values[3],width=5)
            
            self.track_e['values'] = tuple(self.parent.mainwindow.trackcontrol.track.keys())
            
            self.setcursor_b = ttk.Button(self.pframe, text="Set", command=self.marker.start, width=2)
            self.setcursor_dir_b = ttk.Button(self.pframe, text="Dir", command=self.arrow.start, width=2)
            
            self.cursormode_v = tk.StringVar(value='absolute')
            self.cursormode_b_abs = ttk.Radiobutton(self.pframe,text='', variable=self.cursormode_v, value='absolute',command=self.printmode)
            self.cursormode_b_tr  = ttk.Radiobutton(self.pframe,text='' , variable=self.cursormode_v, value='track',command=self.printmode)
            
            self.x_e.grid(column=1, row=row, sticky=(tk.E,tk.W))
            self.y_e.grid(column=2, row=row, sticky=(tk.E,tk.W))
            self.theta_e.grid(column=3, row=row, sticky=(tk.E,tk.W))
            self.track_e.grid(column=4, row=row, sticky=(tk.E,tk.W))
            self.setcursor_b.grid(column=5, row=row, sticky=(tk.E,tk.W))
            self.setcursor_dir_b.grid(column=6, row=row, sticky=(tk.E,tk.W))
            self.cursormode_b_abs.grid(column=7, row=row, sticky=(tk.E,tk.W))
            self.cursormode_b_tr.grid(column=8, row=row, sticky=(tk.E,tk.W))
        def printmode(self):
            print(self.name,self.cursormode_v.get(), self.values[3].get() if self.cursormode_v.get() == 'track' else '')
            
    def __init__(self,mainwindow):
        self.mainwindow = mainwindow
        self.create_widgets()
    def create_widgets(self):
        # マスターウィンドウ作成
        self.master = tk.Toplevel(self.mainwindow)
        self.mainframe = ttk.Frame(self.master, padding='3 3 3 3')
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)
        self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        self.master.title('Measure')

        # カーソル座標フレーム
        self.position_f = ttk.Frame(self.mainframe, padding='3 3 3 3')
        self.position_f.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        self.position_label = {}
        pos = 1
        for i in ['x','y','dir','track',' ',' ','abs','trk']:
            self.position_label[i] = ttk.Label(self.position_f, text=i)
            self.position_label[i].grid(column=pos, row=0, sticky=(tk.E,tk.W))
            pos+=1
        self.cursor_A = self.unit('A',self.mainwindow,self.position_f,self,1,'r')
        self.cursor_B = self.unit('B',self.mainwindow,self.position_f,self,2,'b')
        
        # 測定結果フレーム
        self.result_f = ttk.Frame(self.mainframe, padding='3 3 3 3')
        self.result_f.grid(column=0, row=1, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        self.result_l = {}
        self.result_e = {}
        self.result_v = {}
        pos = 0
        for i in ['distance','direction']:
            self.result_l[i] = ttk.Label(self.result_f, text=i)
            self.result_l[i].grid(column=0, row=pos, sticky=(tk.E,tk.W))
            
            self.result_v[i] = tk.DoubleVar(value=0)
            self.result_e[i] = ttk.Entry(self.result_f, textvariable=self.result_v[i],width=8)
            self.result_e[i].grid(column=1, row=pos, sticky=(tk.E,tk.W))
            pos+=1
            
        # 曲線軌道当てはめフレーム
        self.curvetrack_f = ttk.Frame(self.mainframe, padding='3 3 3 3')
        self.curvetrack_f.grid(column=0, row=2, sticky=(tk.N, tk.W, tk.E, tk.S))
        
        self.curvetrack_value_f = ttk.Frame(self.curvetrack_f, padding='3 3 3 3')
        self.curvetrack_value_f.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.curvetrack_l = {}
        self.curvetrack_e = {}
        self.curvetrack_v = {}
        pos = 0
        for i in ['TC length 1','TC length 2']:
            self.curvetrack_l[i] = ttk.Label(self.curvetrack_value_f, text=i)
            self.curvetrack_l[i].grid(column=0, row=pos, sticky=(tk.E,tk.W))
            
            self.curvetrack_v[i] = tk.DoubleVar(value=0)
            self.curvetrack_e[i] = ttk.Entry(self.curvetrack_value_f, textvariable=self.curvetrack_v[i],width=8)
            self.curvetrack_e[i].grid(column=1, row=pos, sticky=(tk.E,tk.W))
            pos+=1
        self.calc_b = ttk.Button(self.curvetrack_f, text="CurveTrack", command=self.ctfit)
        self.calc_b.grid(column=1, row=0, sticky=(tk.E,tk.W))
        
    def setdistance(self):
        self.result_v['distance'].set(np.sqrt((self.cursor_A.values[0].get()-self.cursor_B.values[0].get())**2+(self.cursor_A.values[1].get()-self.cursor_B.values[1].get())**2))
        self.result_v['direction'].set(self.cursor_B.values[2].get()-self.cursor_A.values[2].get())
    def ctfit(self):
        sv = solver.solver()
        A = np.array([self.cursor_A.values[0].get(),self.cursor_A.values[1].get()])
        B = np.array([self.cursor_B.values[0].get(),self.cursor_B.values[1].get()])
        phiA = np.deg2rad(self.cursor_A.values[2].get())
        phiB = np.deg2rad(self.cursor_B.values[2].get())
        lenTC1 = self.curvetrack_v['TC length 1'].get()
        lenTC2 = self.curvetrack_v['TC length 2'].get()
        tranfunc = 'line'
        
        result = sv.curvetrack_fit(A,phiA,B,phiB,lenTC1,lenTC2,tranfunc)
        
        if not __debug__:
            print(A,phiA,B,phiB,lenTC1,lenTC2,tranfunc)
            print(result)
            
        trackp = trackplot()
        trackp.generate(A,phiA,phiB,result[0],lenTC1,lenTC2,tranfunc)
        print(trackp.result)
        
        ax = self.mainwindow.ax_plane
        ax.plot(trackp.result[:,0],trackp.result[:,1])
        ax.scatter(result[1][0][0],result[1][0][1])
        self.mainwindow.fig_canvas.draw()
            
class curvetrack():
    def __init__(self,mainwindow):
        self.mainwindow = mainwindow

