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

import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import ttk

from kobushi import trackcoordinate

from . import drawcursor
from . import solver
from . import math
from . import curvetrackplot

class interface():
    class unit():
        def __init__(self,name,parentwindow,frame,parent,row,color):
            self.pframe = frame
            self.parentwindow = parentwindow
            self.parent = parent
            self.name = name
            self.marker = drawcursor.marker_pos(self,color=color)
            self.arrow = drawcursor.arrow(self,self.marker)
            
            self.create_widgets(row)
        def create_widgets(self,row):
            self.name_l = ttk.Label(self.pframe, text=self.name)
            self.name_l.grid(column=0, row=row, sticky=(tk.E,tk.W))
            
            self.values = [tk.DoubleVar(value=0),tk.DoubleVar(value=0),tk.DoubleVar(value=0),tk.StringVar(value=''),tk.DoubleVar(value=0)]
            self.values_toshow = [tk.StringVar(value='0'),tk.StringVar(value='0'),tk.StringVar(value='0'),tk.StringVar(value=''),tk.StringVar(value='0')]
            self.coordinate_v = tk.StringVar(value='abs')
            
            self.x_e = ttk.Entry(self.pframe, textvariable=self.values_toshow[0],width=5)
            self.y_e = ttk.Entry(self.pframe, textvariable=self.values_toshow[1],width=5)
            self.theta_e = ttk.Entry(self.pframe, textvariable=self.values_toshow[2],width=5)
            self.track_e = ttk.Combobox(self.pframe, textvariable=self.values[3],width=9)
            self.trackkp_e = ttk.Entry(self.pframe, textvariable=self.values_toshow[4],width=5)
            
            self.make_trackkeylist()
            self.values[3].set('@absolute')
            self.track_e.state(["readonly"])
            
            self.setcursor_b = ttk.Button(self.pframe, text="Pos.", command=self.marker.start, width=4)
            self.setcursor_dir_b = ttk.Button(self.pframe, text="Dir.", command=self.arrow.start, width=4)
            self.setfromval_b = ttk.Button(self.pframe, text="Val.", command=self.setmarkerpos_fromkeyboard, width=4)

            self.relativepos_b = ttk.Checkbutton(self.pframe, text='Rel.', variable=self.coordinate_v, onvalue='rel', offvalue='abs')
            #self.setfromothercursor_b = ttk.Button(self.pframe, text="Offs.", command=None, width=4)

            self.x_e.grid(column=1, row=row, sticky=(tk.E,tk.W))
            self.y_e.grid(column=2, row=row, sticky=(tk.E,tk.W))
            self.theta_e.grid(column=3, row=row, sticky=(tk.E,tk.W))
            self.track_e.grid(column=4, row=row, sticky=(tk.E,tk.W))
            self.trackkp_e.grid(column=5, row=row, sticky=(tk.E,tk.W))
            self.setcursor_b.grid(column=6, row=row, sticky=(tk.E,tk.W))
            self.setcursor_dir_b.grid(column=7, row=row, sticky=(tk.E,tk.W))
            self.setfromval_b.grid(column=8, row=row, sticky=(tk.E,tk.W))
            self.relativepos_b.grid(column=9, row=row, sticky=(tk.E,tk.W))
            #self.setfromothercursor_b.grid(column=9, row=row, sticky=(tk.E,tk.W))
        def printmode(self):
            print(self.name,self.cursormode_v.get(), self.values[3].get() if self.cursormode_v.get() == 'track' else '')
        def setmarkerpos_fromkeyboard(self):
            for i in [0,1,2,4]:
                self.values[i].set(float(self.values_toshow[i].get()))
            self.marker.set_direct()
            self.arrow.set_direct()
        def make_trackkeylist(self):
            currentval = self.values[3].get()
            self.track_e['values'] = tuple(['@absolute'])\
                +tuple(self.parent.mainwindow.trackcontrol.track.keys())\
                +tuple(self.parent.mainwindow.trackcontrol.pointsequence_track.track.keys())
            if currentval not in self.track_e['values']:
                self.values[3].set('@absolute')
    def __init__(self,mainwindow):
        self.mainwindow = mainwindow
        self.master = None
    def create_widgets(self):
        if self.master == None:
            # マスターウィンドウ作成
            self.master = tk.Toplevel(self.mainwindow)
            self.mainframe = ttk.Frame(self.master, padding='3 3 3 3')
            self.mainframe.columnconfigure(0, weight=1)
            self.mainframe.rowconfigure(0, weight=1)
            self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

            self.master.title('Measure')

            self.master.protocol('WM_DELETE_WINDOW', self.closewindow)

            # カーソル座標フレーム
            self.position_f = ttk.Frame(self.mainframe, padding='3 3 3 3')
            self.position_f.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

            self.position_label = {}
            pos = 1
            for i in ['x','y','dir','track','kilopost',' ',' ']:
                self.position_label[i] = ttk.Label(self.position_f, text=i)
                self.position_label[i].grid(column=pos, row=0, sticky=(tk.E,tk.W))
                pos+=1
            self.cursor_A = self.unit('A',self.mainwindow,self.position_f,self,1,'r')
            self.cursor_B = self.unit('B',self.mainwindow,self.position_f,self,2,'b')
            self.cursor_C = self.unit('C',self.mainwindow,self.position_f,self,3,'c')
            self.cursor_D = self.unit('D',self.mainwindow,self.position_f,self,4,'m')
            
            # 測定結果フレーム
            self.result_f = ttk.Frame(self.mainframe, padding='3 3 3 3')
            self.result_f.grid(column=0, row=2, sticky=(tk.N, tk.W, tk.E, tk.S))

            self.result_l = {}
            self.result_e = {}
            self.result_v = {}
            pos = 0
            for i in ['distance','direction']:
                self.result_l[i] = ttk.Label(self.result_f, text=i)
                self.result_l[i].grid(column=pos*2, row=0, sticky=(tk.E,tk.W))

                #self.result_v[i] = tk.DoubleVar(value=0)
                self.result_v[i] = tk.StringVar(value='0')
                self.result_e[i] = ttk.Entry(self.result_f, textvariable=self.result_v[i],width=8)
                self.result_e[i].grid(column=pos*2+1, row=0, sticky=(tk.E,tk.W))
                pos+=1

            self.result_cursor = {'l':{}, 'e':{}, 'v':{}}
            for i in ['from','to']:
                self.result_cursor['l'][i] = ttk.Label(self.result_f, text=i)
                self.result_cursor['l'][i].grid(column=pos*2, row=0, sticky=(tk.E,tk.W))
                self.result_cursor['v'][i] = tk.StringVar()
                self.result_cursor['e'][i] = ttk.Combobox(self.result_f, textvariable=self.result_cursor['v'][i],width=4)
                self.result_cursor['e'][i]['values'] = ('A','B','C','D')
                self.result_cursor['e'][i].grid(column=pos*2+1, row=0, sticky=(tk.E,tk.W))
                self.result_cursor['e'][i].state(["readonly"])
                pos+=1
            self.result_cursor['v']['from'].set('A')
            self.result_cursor['v']['to'].set('B')

            # 直交軌道探索フレーム
            self.nearesttrack_f = ttk.Frame(self.mainframe, padding='3 3 3 3')
            self.nearesttrack_f.grid(column=0, row=4, sticky=(tk.N, tk.W, tk.E, tk.S))

            self.nearesttrack_sel_l = ttk.Label(self.nearesttrack_f, text='Track')
            self.nearesttrack_sel_l.grid(column=2, row=0, sticky=(tk.E,tk.W))
            self.nearesttrack_sel_v = tk.StringVar(value='')
            self.nearesttrack_sel_e = ttk.Combobox(self.nearesttrack_f, textvariable=self.nearesttrack_sel_v,width=8)
            self.nearesttrack_sel_e['values'] = tuple(self.mainwindow.trackcontrol.track.keys())\
                +tuple(self.mainwindow.trackcontrol.pointsequence_track.track.keys())
            self.nearesttrack_sel_e.grid(column=3, row=0, sticky=(tk.E,tk.W))
            self.nearesttrack_sel_e.state(["readonly"])
            
            self.nearesttrack_cursor_l = ttk.Label(self.nearesttrack_f, text='Cursor')
            self.nearesttrack_cursor_l.grid(column=0, row=0, sticky=(tk.E,tk.W))
            self.nearesttrack_cursor_v = tk.StringVar(value='A')
            self.nearesttrack_cursor_e = ttk.Combobox(self.nearesttrack_f, textvariable=self.nearesttrack_cursor_v,width=4)
            self.nearesttrack_cursor_e['values'] = ('A','B','C','D')
            self.nearesttrack_cursor_e.grid(column=1, row=0, sticky=(tk.E,tk.W))
            self.nearesttrack_cursor_e.state(["readonly"])

            self.nearesttrack_doit_btn = ttk.Button(self.nearesttrack_f, text="NearestTrack", command=self.nearesttrack)
            self.nearesttrack_doit_btn.grid(column=4, row=0, sticky=(tk.E,tk.W))

            # カーソル延長線上の距離測定フレーム
            self.alongcursor_f = ttk.Frame(self.mainframe, padding='3 3 3 3')
            self.alongcursor_f.grid(column=0, row=5, sticky=(tk.N, tk.W, tk.E, tk.S))

            self.alongcursor_cursor_l = ttk.Label(self.alongcursor_f, text='Cursor')
            self.alongcursor_cursor_l.grid(column=0, row=0, sticky=(tk.E,tk.W))
            self.alongcursor_cursor_v = tk.StringVar(value='A')
            self.alongcursor_cursor_e = ttk.Combobox(self.alongcursor_f, textvariable=self.alongcursor_cursor_v,width=4)
            self.alongcursor_cursor_e['values'] = ('A','B','C','D')
            self.alongcursor_cursor_e.grid(column=1, row=0, sticky=(tk.E,tk.W))
            self.alongcursor_cursor_e.state(["readonly"])

            self.alongcursor_btn = ttk.Button(self.alongcursor_f, text='//', command=self.distalongcursor)
            self.alongcursor_btn.grid(column=2, row=0, sticky=(tk.E,tk.W))

            self.acrosscursor_btn = ttk.Button(self.alongcursor_f, text='⊥', command=self.distacrosscursor)
            self.acrosscursor_btn.grid(column=3, row=0, sticky=(tk.E,tk.W))

            self.alongcursor_marker = drawcursor.marker_simple(self,self.mainwindow.ax_plane,self.mainwindow.fig_canvas,'g',self.mainwindow.sendtopmost,self.sendtopmost)

            self.alongcursor_dist_l = ttk.Label(self.alongcursor_f, text='distance')
            self.alongcursor_dist_l.grid(column=4, row=0, sticky=(tk.E,tk.W))
            self.alongcursor_dist_v = tk.StringVar(value='0')
            self.alongcursor_dist_e = ttk.Entry(self.alongcursor_f, textvariable=self.alongcursor_dist_v,width=8)
            self.alongcursor_dist_e.grid(column=5, row=0, sticky=(tk.E,tk.W))

            # 曲線軌道当てはめフレーム
            self.curvetrack_f = ttk.Frame(self.mainframe, padding='3 3 3 3')
            self.curvetrack_f.grid(column=0, row=6, sticky=(tk.N, tk.W, tk.E, tk.S))
            self.curvetrack_f['borderwidth'] = 1
            self.curvetrack_f['relief'] = 'solid'

            self.curvetrack_title = ttk.Label(self.curvetrack_f, text='CurveTrack Solver',font=tk.font.Font(weight='bold'))
            self.curvetrack_title.grid(column=0, row=0, sticky=(tk.E,tk.W))

            self.curvetrack_cursor_f = ttk.Frame(self.curvetrack_f, padding='3 3 3 3')
            self.curvetrack_cursor_f.grid(column=3, row=0, sticky=(tk.E,tk.W))
            self.curvetrack_cursor = {'l':{}, 'e':{}, 'v':{}}
            pos=0
            for i in ['α','β','γ']:
                self.curvetrack_cursor['l'][i] = ttk.Label(self.curvetrack_cursor_f, text=i)
                self.curvetrack_cursor['l'][i].grid(column=pos*2, row=0, sticky=(tk.E,tk.W))
                self.curvetrack_cursor['v'][i] = tk.StringVar()
                self.curvetrack_cursor['e'][i] = ttk.Combobox(self.curvetrack_cursor_f, textvariable=self.curvetrack_cursor['v'][i],width=2)
                self.curvetrack_cursor['e'][i]['values'] = ('A','B','C','D')
                self.curvetrack_cursor['e'][i].grid(column=pos*2+1, row=0, sticky=(tk.E,tk.W))
                self.curvetrack_cursor['e'][i].state(["readonly"])
                pos+=1
            self.curvetrack_cursor['v']['α'].set('A')
            self.curvetrack_cursor['v']['β'].set('B')
            self.curvetrack_cursor['v']['γ'].set('C')
            self.curvetrack_cursor_assignresult_v = tk.BooleanVar(value=False)
            self.curvetrack_cursor_assignresult_btn = ttk.Checkbutton(self.curvetrack_cursor_f, text='Assign results to cursor',variable=self.curvetrack_cursor_assignresult_v,onvalue=True,offvalue=False)
            self.curvetrack_cursor_assignresult_btn.grid(column=pos*2+1, row=0, sticky=(tk.E,tk.W))
            
            self.curvetrack_value_f = ttk.Frame(self.curvetrack_f, padding='3 3 3 3')
            self.curvetrack_value_f.grid(column=0, row=1, sticky=(tk.N, tk.W, tk.E, tk.S))
            self.curvetrack_l = {}
            self.curvetrack_e = {}
            self.curvetrack_v = {}
            pos = 0
            for i in ['TCL α','TCL β','CCL', 'R']:
                self.curvetrack_l[i] = ttk.Label(self.curvetrack_value_f, text=i)
                self.curvetrack_l[i].grid(column=pos, row=0, sticky=(tk.E,tk.W))

                self.curvetrack_v[i] = tk.DoubleVar(value=0)
                self.curvetrack_e[i] = ttk.Entry(self.curvetrack_value_f, textvariable=self.curvetrack_v[i],width=8)
                self.curvetrack_e[i].grid(column=pos, row=1, sticky=(tk.E,tk.W))
                pos+=1
            self.curve_transfunc_v = tk.StringVar(value='line')
            
            self.curve_transfunc_f = ttk.Frame(self.curvetrack_f, padding='3 3 3 3')
            self.curve_transfunc_f.grid(column=3, row=1, sticky=(tk.N, tk.W, tk.E, tk.S))
            self.curve_transfunc_line_b = ttk.Radiobutton(self.curve_transfunc_f, text='line', variable=self.curve_transfunc_v, value='line')
            self.curve_transfunc_line_b.grid(column=0, row=0, sticky=(tk.E,tk.W))
            self.curve_transfunc_sin_b = ttk.Radiobutton(self.curve_transfunc_f, text='sin', variable=self.curve_transfunc_v, value='sin')
            self.curve_transfunc_sin_b.grid(column=0, row=2, sticky=(tk.E,tk.W))

            self.curve_fitmode_l = ttk.Label(self.curve_transfunc_f, text='Mode')
            self.curve_fitmode_l.grid(column=1, row=0, sticky=(tk.E))
            self.curve_fitmode_v = tk.StringVar(value='1. α(fix)->β(free), R(free)')
            self.curve_fitmode_box = ttk.Combobox(self.curve_transfunc_f,textvariable=self.curve_fitmode_v)
            self.curve_fitmode_box.grid(column=2, row=0, sticky=(tk.E,tk.W))
            self.curve_fitmode_box['values'] = ('1. α(fix)->β(free), R(free)',\
                                                '2. α(free)->β(fix), R(free)',\
                                                '3. α(free)->β(free), R(fix)',\
                                                '4. α(fix), R(fix), CCL(fix)',\
                                                '5. β(fix), R(fix), CCL(fix)',\
                                                '6. α(fix)->β(free) via γ, R(free)',\
                                                '7. α(free)->β(fix) via γ, R(free)')
            self.curve_fitmode_box.state(["readonly"])
            
            self.calc_b = ttk.Button(self.curve_transfunc_f, text="Do It", command=self.ctfit)
            self.calc_b.grid(column=2, row=2, sticky=(tk.E,tk.W))

            self.calc_mapsyntax_v = tk.BooleanVar(value=True)
            self.calc_mapsyntax_b = ttk.Checkbutton(self.curve_transfunc_f, text='mapsyntax',variable=self.calc_mapsyntax_v,onvalue=True,offvalue=False)
            self.calc_mapsyntax_b.grid(column=1, row=2, sticky=(tk.E,tk.W))

        else:
            self.sendtopmost()
    def closewindow(self):
        self.master.withdraw()
        self.master = None
    def drawall(self):
        if self.master != None:
            for cursorobj in [self.cursor_A, self.cursor_B, self.cursor_C, self.cursor_D]:
                cursorobj.marker.setmarkerobj(pos=True)
                cursorobj.arrow.setobj(None,reset=True)
                cursorobj.arrow.settangent(None,reset=True)

            self.alongcursor_marker.setobj()
    def setdistance(self):
        cursor_obj = {'A':self.cursor_A, 'B':self.cursor_B, 'C':self.cursor_C, 'D':self.cursor_D}
        cursor_f = cursor_obj[self.result_cursor['v']['from'].get()]
        cursor_t = cursor_obj[self.result_cursor['v']['to'].get()]
        
        self.result_v['distance'].set('{:.1f}'.format(np.sqrt((cursor_f.values[0].get()-cursor_t.values[0].get())**2\
                                              +(cursor_f.values[1].get()-cursor_t.values[1].get())**2)))

        self.result_v['direction'].set('{:.1f}'.format(np.rad2deg(math.angle_twov(np.deg2rad(cursor_f.values[2].get()),np.deg2rad(cursor_t.values[2].get())))))
        
    def printdistance(self,mycursor=None):
        cursor_obj = {'A':self.cursor_A, 'B':self.cursor_B, 'C':self.cursor_C, 'D':self.cursor_D}
        cursor_f_name = self.result_cursor['v']['from'].get()
        cursor_t_name = self.result_cursor['v']['to'].get()
        cursor_f = cursor_obj[cursor_f_name]
        cursor_t = cursor_obj[cursor_t_name]

        if mycursor == None or (cursor_f == mycursor or cursor_t == mycursor):
            print()
            print('[Distance between Point {:s} and {:s}]'.format(cursor_f_name,cursor_t_name))
            print('Inputs:')
            print('   Ponint {:s}: ({:f}, {:f}), kp = {:f}'.format(cursor_f_name,cursor_f.values[0].get(),cursor_f.values[1].get(),cursor_f.values[4].get()))
            print('   Ponint {:s}: ({:f}, {:f}), kp = {:f}'.format(cursor_t_name,cursor_t.values[0].get(),cursor_t.values[1].get(),cursor_t.values[4].get()))
            print('Result:')
            print('   distance: {:s}'.format(self.result_v['distance'].get()))
    def printdirection(self,mycursor=None):
        cursor_obj =  {'A':self.cursor_A, 'B':self.cursor_B, 'C':self.cursor_C, 'D':self.cursor_D}
        cursor_f_name = self.result_cursor['v']['from'].get()
        cursor_t_name = self.result_cursor['v']['to'].get()
        cursor_f = cursor_obj[cursor_f_name]
        cursor_t = cursor_obj[cursor_t_name]

        if mycursor == None or (cursor_f == mycursor or cursor_t == mycursor):
            print()
            print('[Direction toward Point {:s} to {:s}]'.format(cursor_f_name,cursor_t_name))
            print('Inputs:')
            print('   Dircection {:s}: {:f}'.format(cursor_f_name,cursor_f.values[2].get()))
            print('   Dircection {:s}: {:f}'.format(cursor_t_name,cursor_t.values[2].get()))
            print('Result:')
            print('   direction:    {:s}'.format(self.result_v['direction'].get()))
    def ctfit(self):
        '''カーソルA, B間を結ぶ最適な曲線軌道を求める
        '''
        cursor_obj =  {'A':self.cursor_A, 'B':self.cursor_B, 'C':self.cursor_C, 'D':self.cursor_D}
        cursor_f_name = self.curvetrack_cursor['v']['α'].get()
        cursor_t_name = self.curvetrack_cursor['v']['β'].get()
        cursor_via_name = self.curvetrack_cursor['v']['γ'].get()
        cursor_f = cursor_obj[cursor_f_name]
        cursor_t = cursor_obj[cursor_t_name]
        cursor_via = cursor_obj[cursor_via_name]
        
        sv = solver.solver()
        A = np.array([cursor_f.values[0].get(),cursor_f.values[1].get()])
        B = np.array([cursor_t.values[0].get(),cursor_t.values[1].get()])
        phiA = np.deg2rad(cursor_f.values[2].get())
        phiB = np.deg2rad(cursor_t.values[2].get())
        lenTC1 = self.curvetrack_v['TCL α'].get()
        lenTC2 = self.curvetrack_v['TCL β'].get()
        lenCC = self.curvetrack_v['CCL'].get()
        R_input = self.curvetrack_v['R'].get()
        tranfunc = self.curve_transfunc_v.get()

        fitmode = self.curve_fitmode_v.get()

        trackp = curvetrackplot.trackplot()
        if fitmode == self.curve_fitmode_box['values'][0]: #'1. α(fix)->β(free), R(free)'
            result = sv.curvetrack_fit(A,phiA,B,phiB,lenTC1,lenTC2,tranfunc)
            trackp.generate(A,phiA,phiB,result[0],lenTC1,lenTC2,tranfunc)
            R_result = result[0]
            CCL_result = trackp.ccl(A,phiA,phiB,result[0],lenTC1,lenTC2,tranfunc)[0]
            shift_result = np.linalg.norm(result[1][0] - B)*np.sign(np.dot(np.array([np.cos(phiB),np.sin(phiB)]),result[1][0] - B))
        elif fitmode == self.curve_fitmode_box['values'][1]: #'2. α(free)->β(fix), R(free)'
            phiA_inv = phiA - np.pi if phiA>0 else phiA + np.pi
            phiB_inv = phiB - np.pi if phiB>0 else phiB + np.pi
            result = sv.curvetrack_fit(B,phiB_inv,A,phiA_inv,lenTC2,lenTC1,tranfunc)
            trackp.generate(B,phiB_inv,phiA_inv,result[0],lenTC2,lenTC1,tranfunc)
            R_result = -result[0]
            CCL_result = -trackp.ccl(A,phiA,phiB,result[0],lenTC1,lenTC2,tranfunc)[0]
            shift_result = np.linalg.norm(result[1][0] - A)*np.sign(np.dot(np.array([np.cos(phiA),np.sin(phiA)]),result[1][0] - A))
        elif fitmode == self.curve_fitmode_box['values'][2]: #'3. α(free)->β(free), R(fix)'
            if False:
                import pdb
                pdb.set_trace()
            result = sv.curvetrack_relocation(A,phiA,B,phiB,lenTC1,lenTC2,tranfunc,R_input)
            A_result = A + np.array([np.cos(phiA),np.sin(phiA)])*result[0]
            R_result = R_input
            trackp.generate(A_result,phiA,phiB,R_input,lenTC1,lenTC2,tranfunc)
            CCL_result = trackp.ccl(A_result,phiA,phiB,R_input,lenTC1,lenTC2,tranfunc)[0]
            shift_result = result[0]
            #print('  x = {:f}'.format(result[0]))
        elif fitmode == self.curve_fitmode_box['values'][3]: #'4. α(fix), R(fix), CCL(fix)'
            phi_end = phiA + lenCC/R_input + trackp.phi_TC(lenTC1, R_input, tranfunc) + trackp.phi_TC(lenTC2, R_input, tranfunc)
            trackp.generate(A, phiA, phi_end, R_input, lenTC1, lenTC2, tranfunc)
            R_result = R_input
            CCL_result = lenCC
            shift_result = 0
        elif fitmode == self.curve_fitmode_box['values'][4]: #'5. β(fix), R(fix), CCL(fix)'
            phi_end = phiB - (lenCC/R_input + trackp.phi_TC(lenTC1, R_input, tranfunc) + trackp.phi_TC(lenTC2, R_input, tranfunc))
            trackp.generate(B, phiB + np.pi if phiB>0 else phiB - np.pi, phi_end + np.pi if phi_end>0 else phi_end - np.pi, -R_input, lenTC2, lenTC1, tranfunc)
            R_result = R_input
            CCL_result = lenCC
            shift_result = 0
        elif fitmode == self.curve_fitmode_box['values'][5]: #'6. α(fix)->β(free) via γ, R(free)'
            if False:
                import pdb
                pdb.set_trace()
            C = np.array([cursor_via.values[0].get(),cursor_via.values[1].get()])
            result = sv.shift_by_TCL(A,phiA,B,phiB,C,tranfunc)
            trackp.generate(A,phiA,phiB,result[1][2],result[0],result[0],tranfunc)
            R_result = result[1][2]
            CCL_result = result[1][1]
            TCL_result = result[0]
            endpoint = trackp.result[-1]
            shift_result = np.linalg.norm(endpoint - B)*np.sign(np.dot(np.array([np.cos(phiB),np.sin(phiB)]),endpoint - B))
            #print(R_result, CCL_result, TCL_result)
            #print('transCL: {:f}, mindist: {:f}, CCL: {:f}, Rtmp: {:f}, num: {:f}'.format(result[0],result[1][0],result[1][1],result[1][2],result[2]))
        elif fitmode == self.curve_fitmode_box['values'][6]: #'7. α(free)->β(fix) via γ, R(free)'
            if False:
                import pdb
                pdb.set_trace()
            phiA_inv = phiA - np.pi if phiA>0 else phiA + np.pi
            phiB_inv = phiB - np.pi if phiB>0 else phiB + np.pi
            C = np.array([cursor_via.values[0].get(),cursor_via.values[1].get()])
            result = sv.shift_by_TCL(B,phiB_inv,A,phiA_inv,C,tranfunc)
            trackp.generate(B,phiB_inv,phiA_inv,result[1][2],result[0],result[0],tranfunc)
            R_result = -result[1][2]
            CCL_result = result[1][1]
            TCL_result = result[0]
            endpoint = trackp.result[-1]
            shift_result = np.linalg.norm(endpoint - A)*np.sign(np.dot(np.array([np.cos(phiA),np.sin(phiA)]),endpoint - A))
        else:
            raise Exception('invalid fitmode')

        # パラメータ、計算結果の印字
        if fitmode == self.curve_fitmode_box['values'][0] or fitmode == self.curve_fitmode_box['values'][1]: #'1 or 2'
            print()
            print('[Curve fitting]')
            print('Inputs:')
            print('   Fitmode:          {:s}'.format(fitmode))
            print('   Cursor α,β:       {:s},{:s}'.format(cursor_f_name,cursor_t_name))
            print('   Ponint α:         ({:f}, {:f})'.format(A[0],A[1]))
            print('   Ponint β:         ({:f}, {:f})'.format(B[0],B[1]))
            print('   Direction α:     {:f}'.format(cursor_f.values[2].get()))
            print('   Direction β:     {:f}'.format(cursor_t.values[2].get()))
            print('   Transition func.: {:s}'.format(tranfunc))
            print('   TCL α:            {:f}'.format(lenTC1))
            print('   TCL β:            {:f}'.format(lenTC2))            
            print('Results:')
            print('   R:   {:f}'.format(R_result))
            print('   CCL: {:f}'.format(CCL_result))
            if fitmode == self.curve_fitmode_box['values'][0]:
                print('   endpt:            ({:f}, {:f})'.format(result[1][0][0],result[1][0][1]))
                print('   shift from pt. β: {:f}'.format(shift_result))
            else:
                print('   startpt:          ({:f}, {:f})'.format(result[1][0][0],result[1][0][1]))
                print('   shift from pt. α: {:f}'.format(shift_result))
        elif fitmode == self.curve_fitmode_box['values'][2]: # 3
            print()
            print('[Curve fitting]')
            print('Inputs:')
            print('   Fitmode:          {:s}'.format(fitmode))
            print('   Cursor α,β:       {:s},{:s}'.format(cursor_f_name,cursor_t_name))
            print('   Ponint α:         ({:f}, {:f})'.format(A[0],A[1]))
            print('   Ponint β:         ({:f}, {:f})'.format(B[0],B[1]))
            print('   Direction α:     {:f}'.format(cursor_f.values[2].get()))
            print('   Direction β:     {:f}'.format(cursor_t.values[2].get()))
            print('   Transition func.: {:s}'.format(tranfunc))
            print('   TCL α:            {:f}'.format(lenTC1))
            print('   TCL β:            {:f}'.format(lenTC2))
            print('   R:                {:f}'.format(R_input))
            print('Results:')
            print('   CCL:        {:f}'.format(CCL_result))
            print('   startpoint: ({:f}, {:f})'.format(A_result[0],A_result[1]))
            print('   shift:      {:f}'.format(shift_result))
        elif fitmode == self.curve_fitmode_box['values'][3] or fitmode == self.curve_fitmode_box['values'][4]: #4, 5
            cursor_label = 'α' if fitmode == self.curve_fitmode_box['values'][3] else 'β'
            print()
            print('[Curve fitting]')
            print('Inputs:')
            print('   Fitmode:          {:s}'.format(fitmode))
            print('   Cursor {:s}:         {:s}'.format(cursor_label,cursor_f_name))
            print('   Ponint {:s}:         ({:f}, {:f})'.format(cursor_label,A[0],A[1]))
            print('   Direction {:s}:      {:f}'.format(cursor_label,cursor_f.values[2].get()))
            print('   Transition func.: {:s}'.format(tranfunc))
            print('   TCL α:            {:f}'.format(lenTC1))
            print('   TCL β:            {:f}'.format(lenTC2))
            print('   CCL:              {:f}'.format(CCL_result))
            print('   R:                {:f}'.format(R_input))
            print('Results:')
            if fitmode == self.curve_fitmode_box['values'][3]:
                print('   endpoint: ({:f}, {:f})'.format(trackp.result[:,0][-1],trackp.result[:,1][-1]))
                print('   phi_end:  {:f}'.format(np.rad2deg(phi_end)))
                
            else:
                print('   startpoint: ({:f}, {:f})'.format(trackp.result[:,0][-1],trackp.result[:,1][-1]))
                print('   phi_start:  {:f}'.format(np.rad2deg(phi_end)))
        elif fitmode == self.curve_fitmode_box['values'][5] or fitmode == self.curve_fitmode_box['values'][6]: #'6'
            print()
            print('[Curve fitting]')
            print('Inputs:')
            print('   Fitmode:          {:s}'.format(fitmode))
            print('   Cursor α,β,γ:     {:s},{:s},{:s}'.format(cursor_f_name,cursor_t_name,cursor_via_name))
            print('   Ponint α:         ({:f}, {:f})'.format(A[0],A[1]))
            print('   Ponint β:         ({:f}, {:f})'.format(B[0],B[1]))
            print('   Ponint γ:         ({:f}, {:f})'.format(C[0],C[1]))
            print('   Direction α:     {:f}'.format(cursor_f.values[2].get()))
            print('   Direction β:     {:f}'.format(cursor_t.values[2].get()))
            print('   Transition func.: {:s}'.format(tranfunc))          
            print('Results:')
            print('   R:   {:f}'.format(R_result))
            print('   CCL: {:f}'.format(CCL_result))
            print('   TCL: {:f}'.format(TCL_result))
            if fitmode == self.curve_fitmode_box['values'][5]:
                endpoint = trackp.result[-1]
                print('   endpt:            ({:f}, {:f})'.format(endpoint[0],endpoint[1]))
                print('   shift from pt. β: {:f}'.format(shift_result))
            else:
                print('   startpt:          ({:f}, {:f})'.format(endpoint[0],endpoint[1]))
                print('   shift from pt. α: {:f}'.format(shift_result))

        # 演算結果をカーソルに設定 (mode4, 5のみ)
        if self.curvetrack_cursor_assignresult_v.get():
            if fitmode == self.curve_fitmode_box['values'][3]:
                tmp_cursor = cursor_t
                tmp_cursor.values[0].set(trackp.result[:,0][-1])
                tmp_cursor.values[1].set(trackp.result[:,1][-1])
                tmp_cursor.values[2].set(np.rad2deg(phi_end))
                tmp_cursor.marker.set_direct()
                tmp_cursor.arrow.set_direct()
            elif fitmode == self.curve_fitmode_box['values'][4]:
                tmp_cursor = cursor_f
                tmp_cursor.values[0].set(trackp.result[:,0][-1])
                tmp_cursor.values[1].set(trackp.result[:,1][-1])
                tmp_cursor.values[2].set(np.rad2deg(phi_end))
                tmp_cursor.marker.set_direct()
                tmp_cursor.arrow.set_direct()
        # 自軌道構文の印字
        if self.calc_mapsyntax_v.get():
            print()
            
            print('$pt_a = {:f};'.format(cursor_f.values[4].get() if cursor_f.values[3].get() != '@absolute' else 0))
            if fitmode == self.curve_fitmode_box['values'][0] or fitmode == self.curve_fitmode_box['values'][5]:
                shift = 0
                print('$pt_a;')
            else:
                shift = shift_result
                print('$pt_a {:s}{:f};'.format('+' if shift>=0 else '',shift))
            print('$cant = 0;')
            print('Curve.SetFunction({:d});'.format(0 if tranfunc == 'sin' else 1))
            print('Curve.Interpolate({:f},0);'.format(0))
            if fitmode == self.curve_fitmode_box['values'][5] or fitmode == self.curve_fitmode_box['values'][6]:
                lenTC_result = {'1':TCL_result, '2':TCL_result}
            else:
                lenTC_result = {'1':lenTC1, '2':lenTC2}
            if lenTC_result['1'] != 0 or True:
                tmp = shift + lenTC_result['1']
                print('$pt_a {:s}{:f};'.format('+' if tmp>=0 else '', tmp))
            print('Curve.Interpolate({:f}, $cant);'.format(R_result))
            tmp = (shift + lenTC_result['1'] + CCL_result)
            print('$pt_a {:s}{:f};'.format('+' if tmp>=0 else '', tmp))
            print('Curve.Interpolate({:f}, $cant);'.format(R_result))
            if lenTC_result['2'] != 0 or True:
                tmp = (shift + lenTC_result['1'] + CCL_result + lenTC_result['2'])
                print('$pt_a {:s}{:f};'.format('+' if tmp>=0 else '', tmp))
            print('Curve.Interpolate({:f},0);'.format(0))
            
        ax = self.mainwindow.ax_plane
        ax.plot(trackp.result[:,0],trackp.result[:,1])
        '''
        if not __debug__:
            ax.scatter(result[1][0][0],result[1][0][1])
        '''
        self.mainwindow.fig_canvas.draw()
    def nearesttrack(self):
        '''指定した軌道上のカーソルAに最も近い点を求める
        '''
        cursor = self.nearesttrack_cursor_v.get()
        cursor_obj = {'A':self.cursor_A, 'B':self.cursor_B, 'C':self.cursor_C, 'D':self.cursor_D}
        
        inputpos = np.array([cursor_obj[cursor].values[0].get(),cursor_obj[cursor].values[1].get()])
        trackkey = self.nearesttrack_sel_v.get()
        if '@' not in trackkey:
            track = self.mainwindow.trackcontrol.track[trackkey]['result']
        else:
            track = self.mainwindow.trackcontrol.pointsequence_track.track[trackkey]['result']
        track_pos = track[:,1:3]

        result = math.minimumdist(track_pos, inputpos)
        kilopost = math.cross_kilopost(track, result)
            
        print()
        print('[Distance nearest point along the track]')
        print('Inputs')
        print('   Ponint {:s}: ({:f}, {:f})'.format(cursor,inputpos[0],inputpos[1]))
        print('   Trakckey: {:s}'.format(self.nearesttrack_sel_v.get())) 
        print('Results')
        print('   distance: {:f}, kilopost: {:f}'.format(result[0], kilopost))

        ax = self.mainwindow.ax_plane
        ax.scatter(track[result[2]][1],track[result[2]][2])
        ax.plot([inputpos[0],result[1][0]],[inputpos[1],result[1][1]])
        self.mainwindow.fig_canvas.draw()

    def distalongcursor(self):
        '''カーソルAの延長線上の任意の点との距離を求める
        '''
        cursor = self.alongcursor_cursor_v.get()
        cursor_obj = {'A':self.cursor_A, 'B':self.cursor_B, 'C':self.cursor_C, 'D':self.cursor_D}
        
        sourcepos = np.array([cursor_obj[cursor].values[0].get(),cursor_obj[cursor].values[1].get()])
        sourcedir = np.deg2rad(cursor_obj[cursor].values[2].get())
        def alongf(x,y,spos,sdir):
            unitv = np.array([np.cos(sdir),np.sin(sdir)])
            pointed = np.array([x,y])-spos
            result = spos + unitv*np.dot(unitv,pointed)
            self.alongcursor_dist_v.set('{:.3f}'.format(np.linalg.norm(result-spos)))
            return (result[0],result[1])
        def printpos(self,spos):
            print('Result')
            print('   position:     ({:f}, {:f})'.format(self.xout,self.yout))
            print('   distance:     {:f}'.format(np.sqrt((self.xout-sourcepos[0])**2+(self.yout-sourcepos[1])**2)))
        self.alongcursor_marker.start(lambda x,y: alongf(x,y,sourcepos,sourcedir),lambda self: printpos(self,sourcepos))
        print()
        print('[distance // cursor {:s}]'.format(cursor))
        print('Inputs')
        print('   Ponint {:s}:     ({:f}, {:f})'.format(cursor,sourcepos[0],sourcepos[1]))
        print('   Dircection {:s}: {:f}'.format(cursor,cursor_obj[cursor].values[2].get()))
    def distacrosscursor(self):
        '''カーソルAの法線上の任意の点との距離を求める
        '''
        cursor = self.alongcursor_cursor_v.get()
        cursor_obj = {'A':self.cursor_A, 'B':self.cursor_B, 'C':self.cursor_C, 'D':self.cursor_D}
        
        sourcepos = np.array([cursor_obj[cursor].values[0].get(),cursor_obj[cursor].values[1].get()])
        sourcedir = np.deg2rad(cursor_obj[cursor].values[2].get())
        def alongf(x,y,spos,sdir):
            unitv = np.array([np.cos(sdir-np.pi/2),np.sin(sdir-np.pi/2)])
            pointed = np.array([x,y])-spos
            result = spos + unitv*np.dot(unitv,pointed)
            self.alongcursor_dist_v.set('{:.3f}'.format(np.linalg.norm(result-spos)))
            return (result[0],result[1])
        def printpos(self,spos):
            print('Result')
            print('   position:     ({:f}, {:f})'.format(self.xout,self.yout))
            print('   distance:     {:f}'.format(np.sqrt((self.xout-sourcepos[0])**2+(self.yout-sourcepos[1])**2)))
        self.alongcursor_marker.start(lambda x,y: alongf(x,y,sourcepos,sourcedir),lambda self: printpos(self,sourcepos))
        print()
        print('[distance ⊥ cursor {:s}]'.format(cursor))
        print('Inputs')
        print('   Ponint {:s}:     ({:f}, {:f})'.format(cursor,sourcepos[0],sourcepos[1]))
        print('   Dircection {:s}: {:f}'.format(cursor,cursor_obj[cursor].values[2].get()))
    def sendtopmost(self,event=None):
        self.master.lift()
        self.master.focus_force()
    def setmarkerpos_fromkeyboard(self):
        for marker in [self.cursor_A, self.cursor_B]:
            for i in [0,1,2,4]:
                marker.values[i].set(float(marker.values_toshow[i].get()))
            marker.marker.set_direct()
            marker.arrow.set_direct()
    def reload_trackkeys(self):
        if self.master is not None:
            for marker in [self.cursor_A, self.cursor_B, self.cursor_C, self.cursor_D]:
                marker.make_trackkeylist()
                
