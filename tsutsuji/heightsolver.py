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
import numpy as np
import tkinter as tk
from tkinter import ttk
import tkinter.colorchooser as colorchooser
import tkinter.scrolledtext as scrolledtext
import re
import itertools
import xml.etree.ElementTree as ET

from kobushi import trackcoordinate

from . import drawcursor
from . import math
from . import solver
from . import curvetrackplot



class solverDataManager():
    class solverDataElement():
        def __init__(self, id, trackcolor, trackpos, syntax_str, params_str, plotobj = None):
            self.id = id
            self.trackcolor = trackcolor

            self.trackpos = trackpos
            self.syntax_str = syntax_str
            self.params_str = params_str

            self.plotobj = plotobj
    def __init__(self, ax, fig_canvas):
        self.coloriter = itertools.cycle(['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd','#8c564b','#e377c2','#7f7f7f','#bcbd22','#17becf'])
        self.iditer = itertools.count(0)
        self.data = {}

        self.ax = ax
        self.fig_canvas = fig_canvas
    def add(self, trackpos, syntax_str, params_str, id=None, trackcolor=None):
        if id is None:
            id = str(next(self.iditer))
        if trackcolor is None:
            trackcolor = next(self.coloriter)

        self.data[id] = self.solverDataElement(id, trackcolor, trackpos, syntax_str, params_str)
        return id, trackcolor
    def delete(self, id):
        plotobj = self.data[id].plotobj
        plotobj.remove()
        del self.data[id]
        self.fig_canvas.draw()
    def set_trackcolor(self, id, color=None):
        if color is None:
            color = colorchooser.askcolor(color=self.data[id].trackcolor)
        self.data[id].trackcolor = color[1]
    def plot_track(self, id):
        self.data[id].plotobj, = self.ax.plot(self.data[id].trackpos[:,0],self.data[id].trackpos[:,1],color = self.data[id].trackcolor)
        self.fig_canvas.draw()
    def replot_all(self):
        if self.ax is not None and self.fig_canvas is not None:
            for id in self.data.keys():
                self.data[id].plotobj, = self.ax.plot(self.data[id].trackpos[:,0],self.data[id].trackpos[:,1],color = self.data[id].trackcolor)
            self.fig_canvas.draw()
    def set_plotcolor(self, id, color=None):
        self.set_trackcolor(id,color)
        self.data[id].plotobj.set_color(self.data[id].trackcolor)
        self.fig_canvas.draw()
    

        
        
class heightSolverUI():
    def __init__(self, parent, cursorobj, ax, fig_canvas):
        self.parentframe = parent
        self.cursorobj = cursorobj
        self.solver = solver.solver()
        self.slgen = curvetrackplot.slopetrackplot()
        self.ax = ax
        self.fig_canvas = fig_canvas
        self.solverdata = solverDataManager(self.ax, self.fig_canvas)
    def create_widget(self, parentframe, ax, fig_canvas):
        self.parentframe = parentframe
        self.ax = ax
        self.fig_canvas = fig_canvas
        self.solverdata.ax = self.ax
        self.solverdata.fig_canvas = self.fig_canvas
        self.parentframe['borderwidth'] = 1
        self.parentframe['relief'] = 'solid'
        self.title = ttk.Label(self.parentframe, text='Gradient Solver',font=tk.font.Font(weight='bold'))
        self.title.grid(column=0, row=0, sticky=(tk.E,tk.W))
        self.parentframe.columnconfigure(2, weight=1)

        self.controlframe = ttk.Frame(self.parentframe, padding='3 3 3 3')
        self.controlframe.grid(column=0, row=1, sticky=(tk.E,tk.W))

        self.cursorframe = ttk.Frame(self.controlframe, padding='3 3 3 3')
        self.cursorframe.grid(column=1, row=0, sticky=(tk.E))
        
        self.cursor_vals = ('α', 'β', 'γ')
        self.cursor_widgets = {}
        pos=0
        for key in self.cursor_vals:
            self.cursor_widgets[key] = {}
            self.cursor_widgets[key]['label'] = ttk.Label(self.cursorframe, text=key)
            self.cursor_widgets[key]['label'].grid(column=pos*2, row=0, sticky=(tk.E,tk.W))
            self.cursor_widgets[key]['var'] = tk.StringVar()
            self.cursor_widgets[key]['cb'] = ttk.Combobox(self.cursorframe, textvariable=self.cursor_widgets[key]['var'], width=5)
            self.cursor_widgets[key]['cb'].grid(column=pos*2+1, row=0, sticky=(tk.E,tk.W))
            pos+=1
            self.cursor_widgets[key]['cb'].state(["readonly"])
        self.make_cursorlist()

        self.paramsframe = ttk.Frame(self.controlframe, padding='3 3 3 3')
        self.paramsframe.grid(column=0, row=1, sticky=(tk.E,tk.W))

        self.params_vals = ('VCL α', 'VCL β', 'R α', 'R β')#, 'Gr. 1')
        self.params_widgets = {}
        pos=0
        row=0
        for key in self.params_vals:
            self.params_widgets[key] = {}
            self.params_widgets[key]['label'] = ttk.Label(self.paramsframe, text=key)
            self.params_widgets[key]['label'].grid(column=pos, row=row*2, sticky=(tk.E,tk.W))
            self.params_widgets[key]['var'] = tk.DoubleVar()
            self.params_widgets[key]['ent'] = ttk.Entry(self.paramsframe, textvariable=self.params_widgets[key]['var'],width=8)
            self.params_widgets[key]['ent'].grid(column=pos, row=row*2+1, sticky=(tk.E,tk.W))
            pos+=1
            if pos%4 == 0:
                pos = 0
                row+=1

        self.modeframe = ttk.Frame(self.controlframe, padding='3 3 3 3')
        self.modeframe.grid(column=1, row=1, sticky=(tk.E))

        self.fitmode_label = ttk.Label(self.modeframe,text='mode')
        self.fitmode_label.grid(column=0, row=0, sticky=(tk.E))
        self.fitmode_list = ('1. α->β, given VCLα',\
                             '2. α->β, given Rα',\
                             '3. α->β->γ, given VCLα,β',\
                             '4. α->β->γ, given Rα,β',)
        self.fitmode_v = tk.StringVar(value=self.fitmode_list[0])
        self.fitmode_cb = ttk.Combobox(self.modeframe,textvariable=self.fitmode_v,height=len(self.fitmode_list),width=28)
        self.fitmode_cb.grid(column=1, row=0, sticky=(tk.E))
        self.fitmode_cb['values'] = self.fitmode_list
        self.fitmode_cb.state(["readonly"])

        self.doit_b = ttk.Button(self.modeframe, text='Do It',command=self.execsolver)
        self.doit_b.grid(column=1, row=1, sticky=(tk.E,tk.W))

        self.mapsyntax_v = tk.BooleanVar(value=True)
        self.mapsyntax_b = ttk.Checkbutton(self.modeframe, text='mapsyntax', variable=self.mapsyntax_v,onvalue=True,offvalue=False)
        self.mapsyntax_b.grid(column=0, row=1, sticky=(tk.E))

        self.managerframe = ttk.Frame(self.parentframe, padding='3 3 3 3')
        self.managerframe.grid(column=0, row=2, sticky=(tk.E,tk.W))

        self.solverdatatreeframe = ttk.Frame(self.managerframe, padding='3 3 3 3')
        self.solverdatatreeframe.grid(column=1, row=0, sticky=(tk.N,tk.W,tk.E,tk.S))

        self.solverdatatree = ttk.Treeview(self.solverdatatreeframe, column=('Color'), height=5)
        self.solverdatatree.grid(column=0,row=0, sticky=(tk.E, tk.W))

        self.solverdatatree.bind('<<TreeviewSelect>>',self.click_solverdatatree)
        self.solverdatatree.column('#0',width=50)
        self.solverdatatree.column('Color',width=50)
        self.solverdatatree.heading('#0',text='ID')
        self.solverdatatree.heading('Color',text='Color')

        self.solverdatatree_scrollbar = ttk.Scrollbar(self.solverdatatreeframe, orient=tk.VERTICAL, command=self.solverdatatree.yview)
        self.solverdatatree_scrollbar.grid(column=1,row=0,sticky=(tk.N,tk.W,tk.E,tk.S))
        self.solverdatatree.configure(yscrollcommand=self.solverdatatree_scrollbar.set)

        for id in self.solverdata.data.keys():
            color = self.solverdata.data[id].trackcolor
            self.solverdatatree.insert('','end',iid=id,text=id,values=(color))

        self.managerbuttonsframe = ttk.Frame(self.solverdatatreeframe, padding='3 3 3 3')
        self.managerbuttonsframe.grid(column=0, row=1, sticky=(tk.W,tk.E))

        self.manager_del_b = ttk.Button(self.managerbuttonsframe, text='Delete',command=self.delete_solverdatatree_data)
        self.manager_del_b.grid(column=1, row=0, sticky=(tk.N,tk.W,tk.E,tk.S))
        self.manager_color_b = ttk.Button(self.managerbuttonsframe, text='Color',command=self.set_solverdatatree_color)
        self.manager_color_b.grid(column=0, row=0, sticky=(tk.N,tk.W,tk.E,tk.S))
        '''
        self.manager_xml_b = ttk.Button(self.managerbuttonsframe, text='XML', command=self.save_solverdata_xml)
        self.manager_xml_b.grid(column=2,row=0, sticky=(tk.N,tk.W,tk.E,tk.S))
        self.manager_xmlread_b = ttk.Button(self.managerbuttonsframe, text='XMLread', command=self.load_solverdata_xml)
        self.manager_xmlread_b.grid(column=3,row=0, sticky=(tk.N,tk.W,tk.E,tk.S))
        '''

        self.textboxframe =  ttk.Frame(self.managerframe, padding='3 3 3 3')
        self.textboxframe.grid(column=0, row=0, sticky=(tk.N,tk.W,tk.E,tk.S))

        self.paramsboxlabelframe = ttk.Frame(self.textboxframe, padding='3 3 3 3')
        self.paramsboxlabelframe.grid(column=0,row=0, sticky=(tk.N,tk.W,tk.E,tk.S))
        self.paramsboxlabel = ttk.Label(self.paramsboxlabelframe, text='Parameters',font=tk.font.Font(weight='bold'))
        self.paramsboxlabel.grid(column=0,row=0, sticky=(tk.N,tk.W,tk.E,tk.S))
        self.paramsbox = scrolledtext.ScrolledText(self.textboxframe,width=60,height=4)#,state='disabled')
        self.paramsbox.grid(column=0,row=1, sticky=(tk.N,tk.W,tk.E,tk.S))

        self.copyparams_b = ttk.Button(self.paramsboxlabelframe, text='Copy params', command = lambda: self.setClipboard(self.paramsbox.get("1.0", "end-1c")))
        self.copyparams_b.grid(column=1,row=0, sticky=(tk.N,tk.W,tk.E,tk.S))

        self.syntaxboxlabelframe = ttk.Frame(self.textboxframe, padding='3 3 3 3')
        self.syntaxboxlabelframe.grid(column=0,row=2, sticky=(tk.N,tk.W,tk.E,tk.S))
        self.syntaxboxlabel = ttk.Label(self.syntaxboxlabelframe, text='Syntax',font=tk.font.Font(weight='bold'))
        self.syntaxboxlabel.grid(column=0,row=0, sticky=(tk.N,tk.W,tk.E,tk.S))
        self.syntaxbox = scrolledtext.ScrolledText(self.textboxframe,width=60,height=4)#,state='disabled')
        self.syntaxbox.grid(column=0,row=3, sticky=(tk.N,tk.W,tk.E,tk.S))
        
        self.copysyntax_b = ttk.Button(self.syntaxboxlabelframe, text='Copy syntax', command = lambda: self.setClipboard(self.syntaxbox.get("1.0", "end-1c")))
        self.copysyntax_b.grid(column=1,row=0, sticky=(tk.N,tk.W,tk.E,tk.S))

        
            
    def make_cursorlist(self):
        for key in self.cursor_vals:
            #currentval = self.cursor_widgets[key]['var'].get()
            self.cursor_widgets[key]['cb']['values'] = tuple(self.cursorobj.keys())
    def execsolver(self):
        mode = self.fitmode_v.get()
        iid_A = self.cursor_widgets['α']['var'].get()
        iid_B = self.cursor_widgets['β']['var'].get()
        iid_C = self.cursor_widgets['γ']['var'].get()

        lenVC_A = self.params_widgets['VCL α']['var'].get()
        lenVC_B = self.params_widgets['VCL β']['var'].get()
        #grad1 = self.params_widgets['Gr. 1']['var'].get()
        RA = self.params_widgets['R α']['var'].get()
        RB = self.params_widgets['R β']['var'].get()
   
        cursor_tmp = self.cursorobj[iid_A].values
        pos_tmp = np.array([cursor_tmp['Distance'],cursor_tmp['Height']])
        phi_tmp = cursor_tmp['Angle']
        posA = pos_tmp
        phiA = phi_tmp
        grA = cursor_tmp['Gradient']

        cursor_tmp = self.cursorobj[iid_B].values
        pos_tmp = np.array([cursor_tmp['Distance'],cursor_tmp['Height']])
        phi_tmp = cursor_tmp['Angle']
        posB = pos_tmp
        phiB = phi_tmp
        grB = cursor_tmp['Gradient']

        if '1.' in mode or '2.' in mode:
            if '1.' in mode:
                RA = lenVC_A/(phiB - phiA)
            else:
                if (phiB - phiA)<0:
                    RA = abs(RA)*(-1)
                else:
                    RA = abs(RA)
                lenVC_A = RA*(phiB - phiA)

            if lenVC_A != 0:
                result = self.solver.curvetrack_relocation(posA,phiA,posB,phiB,0,0,'line',RA)
            else:
                result = math.crosspoint_2lines(posA,math.phi2el(phiA),posB,math.phi2el(phiB))

            trackpos = self.slgen.generate_single(posA,phiA,posB,phiB,lenVC_A,slen=result[0])
            #self.ax.plot(trackpos[:,0], trackpos[:,1])
            #self.fig_canvas.draw()

            param_str = self.gen_paramstr_single(mode, result, iid_A, iid_B, posA, posB, lenVC_A, RA)
            #print()
            #print(param_str)

            #if self.mapsyntax_v.get():
            mapsyntax = self.generate_mapsyntax_single(result, posA[0], grA, grB, lenVC_A)
            #print(mapsyntax)
        elif '3.' in mode or '4.' in mode:
            cursor_tmp = self.cursorobj[iid_C].values
            pos_tmp = np.array([cursor_tmp['Distance'],cursor_tmp['Height']])
            phi_tmp = cursor_tmp['Angle']
            posC = pos_tmp
            phiC = phi_tmp
            grC = cursor_tmp['Gradient']

            if '3.' in mode:
                RA = lenVC_A/(phiB - phiA)
                RB = lenVC_B/(phiC - phiB)
            else:
                if (phiB - phiA)<0:
                    RA = abs(RA)*(-1)
                else:
                    RA = abs(RA)
                if (phiC - phiB)<0:
                    RB = abs(RB)*(-1)
                else:
                    RB = abs(RB)
                lenVC_A = RA*(phiB - phiA)
                lenVC_B = RB*(phiC - phiB)

            if lenVC_A != 0:
                resultA = self.solver.curvetrack_relocation(posA,phiA,posB,phiB,0,0,'line',RA)
            else:
                resultA = math.crosspoint_2lines(posA,math.phi2el(phiA),posB,math.phi2el(phiB))
            trackposA = self.slgen.generate_single(posA,phiA,posB,phiB,lenVC_A,slen=resultA[0])

            if lenVC_B != 0:
                resultB = self.solver.curvetrack_relocation(posB,phiB,posC,phiC,0,0,'line',RB)
            else:
                resultB = math.crosspoint_2lines(posB,math.phi2el(phiB),posC,math.phi2el(phiC))
            trackposB = self.slgen.generate_single(posB,phiB,posC,phiC,lenVC_B,slen=resultB[0])

            trackpos = np.vstack((trackposA,trackposB))

            param_str = self.gen_paramstr_double(mode, resultA, resultB, iid_A, iid_B, iid_C, posA, posB, posC, lenVC_A, lenVC_B, RA, RB)#, len_endslopeAtoB)

            mapsyntax = self.generate_mapsyntax_single(resultA, posA[0], grA, grB, lenVC_A)
            mapsyntax += self.generate_mapsyntax_single(resultB, posB[0], grB, grC, lenVC_B)

        id, color = self.solverdata.add(trackpos, mapsyntax, param_str)
        self.solverdata.plot_track(id)

        self.solverdatatree.insert('','end',iid=id,text=id,values=(color))
        self.solverdatatree.focus(item=id)
        self.solverdatatree.selection_set(id)
        
    def generate_mapsyntax_single(self, result, distA, grA, grB, lenVC_A):
        syntax_str = ''
        syntax_str += '$pt_a = {:f};'.format(distA) + '\n'

        shift = result[0]
        tmp_dist = shift
        syntax_str += '$pt_a {:s}{:f};'.format('+' if tmp_dist>=0 else '',tmp_dist) + '\n'

        syntax_str += 'Gradient.Interpolate({:f});'.format(grA)+'\n'

        tmp_dist = shift + lenVC_A
        syntax_str += '$pt_a {:s}{:f};'.format('+' if tmp_dist>=0 else '',tmp_dist) + '\n'

        syntax_str += 'Gradient.Interpolate({:f});'.format(grB)+'\n'

        return syntax_str
    def gen_paramstr_single(self, fitmode, result, iidA, iidB, posA, posB, lenVC_A, R_A):
        param_str = ''

        #param_str += '\n'
        param_str += '[Gradient fitting]\n'
        param_str += 'Inputs:\n'
        param_str += '   Fitmode:          {:s}\n'.format(fitmode)
        param_str += '   Cursor values:    (Distance, Gradient)\n'
        param_str += '      α ({:s}):      ({:f}, {:f})\n'.format(iidA,posA[0],posA[1])
        param_str += '      β ({:s}):      ({:f}, {:f})\n'.format(iidB,posB[0],posB[1])
        param_str += '   VCL α:            {:f}\n'.format(lenVC_A)
        param_str += '      (RVC α:        {:f})\n'.format(R_A)
        param_str += 'Results:\n'
        #param_str += '   startPt:          ({:f}, {:f})\n'.format(result[1][0][0], result[1][0][1])
        param_str += '   shift from pt. α: {:f}\n'.format(result[0])
        return param_str
    def gen_paramstr_double(self, fitmode, resultA, resultB, iidA, iidB, iidC, posA, posB, posC, lenVC_A, lenVC_B, R_A, R_B):
        param_str = ''

        #param_str += '\n'
        param_str += '[Gradient fitting]\n'
        param_str += 'Inputs:\n'
        param_str += '   Fitmode:          {:s}\n'.format(fitmode)
        param_str += '   Cursor values:    (Distance, Gradient)\n'
        param_str += '      α ({:s}):      ({:f}, {:f})\n'.format(iidA,posA[0],posA[1])
        param_str += '      β ({:s}):      ({:f}, {:f})\n'.format(iidB,posB[0],posB[1])
        param_str += '      γ ({:s}):      ({:f}, {:f})\n'.format(iidC,posC[0],posC[1])
        param_str += '   VCL α:            {:f}\n'.format(lenVC_A)
        param_str += '      (RVC α:        {:f})\n'.format(R_A)
        param_str += '   VCL β:            {:f}\n'.format(lenVC_B)
        param_str += '      (RVC β:        {:f})\n'.format(R_B)
        param_str += 'Results:\n'
        #param_str += '   startPt:          ({:f}, {:f})\n'.format(result[1][0][0], result[1][0][1])
        param_str += '   shift from pt. α: {:f}\n'.format(resultA[0])
        param_str += '   shift from pt. β: {:f}\n'.format(resultB[0])
        return param_str
    def click_solverdatatree(self,event=None):
        if event is not None:
            id = self.solverdatatree.focus()
            self.paramsbox.delete(0.,tk.END)
            self.syntaxbox.delete(0.,tk.END)
            if id in self.solverdata.data.keys():
                self.paramsbox.insert(0.,self.solverdata.data[id].params_str)
                self.syntaxbox.insert(0.,self.solverdata.data[id].syntax_str)
    def set_solverdatatree_color(self,event=None):
        id = self.solverdatatree.focus()
        self.solverdata.set_plotcolor(id)
        self.solverdatatree.item(id,values=(self.solverdata.data[id].trackcolor))
    def delete_solverdatatree_data(self,event=None):
        id = self.solverdatatree.focus()
        self.solverdatatree.delete(id)
        self.solverdata.delete(id)
    def replot(self):
        self.solverdata.replot_all()
    def save_solverdata_xml(self,base):
        root = ET.SubElement(base,'SolverData')
        for id in self.solverdata.data.keys():
            data = self.solverdata.data[id]
            parent = ET.SubElement(root, 'Height')
            elem_id = ET.SubElement(parent, 'id')
            elem_id.text = id

            elem_trackcolor = ET.SubElement(parent, 'trackcolor')
            elem_trackcolor.text = data.trackcolor

            elem_trackpos = ET.SubElement(parent, 'trackpos')
            for i in data.trackpos:
                tmp_elem = ET.SubElement(elem_trackpos, 'position')
                tmp_elem.text = '{:f}, {:f}'.format(i[0],i[1])

            elem_syntax_str = ET.SubElement(parent, 'syntax_str')
            elem_syntax_str.text = '{:s}'.format(data.syntax_str)

            elem_params_str = ET.SubElement(parent, 'params_str')
            elem_params_str.text =  '{:s}'.format(data.params_str)
        return base
    def load_solverdata_xml(self,root):
        for SolverData in root.iter('SolverData'):
            for Height in SolverData.iter('Height'):
                id = Height.find('id').text
                trackcolor = Height.find('trackcolor').text
                syntax_str = Height.find('syntax_str').text
                params_str = Height.find('params_str').text

                trackpos_parent = Height.find('trackpos')
                trackpos = []
                for pos_elem in trackpos_parent.iter('position'):
                    #print(trackpos_elem)
                    elem_split = pos_elem.text.split(',')
                    trackpos.append([float(elem_split[0]), float(elem_split[1])])
                trackpos = np.array(trackpos)

                self.solverdata.add(trackpos, syntax_str, params_str, id=id, trackcolor=trackcolor)

                self.solverdata.plot_track(id)
                self.solverdatatree.insert('','end',iid=id,text=id,values=(trackcolor))        
    def setClipboard(self, string):
        self.parentframe.clipboard_clear()
        self.parentframe.clipboard_append(string)
