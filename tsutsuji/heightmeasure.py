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
import re

from kobushi import trackcoordinate

from . import drawcursor
'''
from . import solver
from . import math
from . import curvetrackplot
'''

class Interface():
    class unitCursor():
        def __init__(self,id,parent,ax,canvas,color,ch_main,ch_measure):
            self.id = id
            self.marker = drawcursor.marker_simple(parent,ax,canvas,color,ch_main,ch_measure)
    def __init__(self,mainwindow):
        self.mainwindow = mainwindow
        self.master = None
        #self.trackcontrol = self.mainwindow.trackcontrol
        self.cursorlist_column = ('Track', 'Distance', 'Height', 'Gradient')
        self.cursors = {}
    def create_window(self):
        if self.master is None:
            self.master = tk.Toplevel(self.mainwindow.master)
            self.master.title('Measure (Height)')
            self.master.protocol('WM_DELETE_WINDOW', self.closewindow)
            self.master.columnconfigure(0, weight=1)
            self.master.rowconfigure(0, weight=1)
            
            self.mainframe = ttk.Frame(self.master, padding = '3 3 3 3')
            self.mainframe.columnconfigure(0, weight=1)
            self.mainframe.rowconfigure(0, weight=1)
            self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
            
            self.create_widgets()
            self.make_trackkeylist()
        else:
            self.sendtopmost()
    def create_widgets(self):
        self.cursorlist = ttk.Treeview(self.mainframe, column=self.cursorlist_column,height=5)
        self.cursorlist.column('#0',width=40)
        self.cursorlist.column('Track',width=100)
        self.cursorlist.column('Distance',width=80)
        self.cursorlist.column('Height',width=80)
        self.cursorlist.column('Gradient',width=80)
        self.cursorlist.heading('#0',text='ID')
        self.cursorlist.heading('Track',text='Track')
        self.cursorlist.heading('Distance',text='Distance')
        self.cursorlist.heading('Height',text='Height')
        self.cursorlist.heading('Gradient',text='Gradient')
        
        self.cursorlist.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

        self.edit_frame = ttk.Frame(self.mainframe, padding='3 3 3 3')
        self.edit_frame.grid(column=0, row=1,sticky=(tk.E, tk.W))

        edit_vals = ('ID', 'Track', 'Distance', 'Height', 'Gradient')
        self.edit_labels = {}
        self.edit_entries = {}
        self.edit_vals = {}

        for i in edit_vals:
            self.edit_labels[i] = ttk.Label(self.edit_frame, text=i)

        i = 'ID'
        self.edit_vals[i] = tk.StringVar(value='')
        self.edit_entries[i] = ttk.Entry(self.edit_frame, textvariable = self.edit_vals[i],width=5)

        i = 'Track'
        self.edit_vals[i] = tk.StringVar(value='')
        self.edit_entries[i] = ttk.Combobox(self.edit_frame, textvariable = self.edit_vals[i],width=10)

        i = 'Distance'
        self.edit_vals[i] = tk.DoubleVar(value=0)
        self.edit_entries[i] = ttk.Entry(self.edit_frame, textvariable = self.edit_vals[i],width=10)

        i = 'Height'
        self.edit_vals[i] = tk.DoubleVar(value=0)
        self.edit_entries[i] = ttk.Entry(self.edit_frame, textvariable = self.edit_vals[i],width=10)

        i = 'Gradient'
        self.edit_vals[i] = tk.DoubleVar(value=0)
        self.edit_entries[i] = ttk.Entry(self.edit_frame, textvariable = self.edit_vals[i],width=10)

        j = 0
        for i in edit_vals:
            self.edit_labels[i].grid(column=j, row=0,sticky=(tk.E, tk.W))
            self.edit_entries[i].grid(column=j, row=1,sticky=(tk.E, tk.W))
            j+=1

        self.button_frame = ttk.Frame(self.mainframe, padding='3 3 3 3')
        self.button_frame.grid(column=0, row=2,sticky=(tk.E, tk.W))

        self.add_b = ttk.Button(self.button_frame, text='Add', command=self.addcursor)
        self.del_b = ttk.Button(self.button_frame, text='Delete', command=self.deletecursor)

        self.add_b.grid(column=0, row=0,sticky=(tk.N, tk.E, tk.W))
        self.del_b.grid(column=1, row=0,sticky=(tk.N, tk.E, tk.W))
        
    def closewindow(self):
        if self.master is not None:
            self.master.withdraw()
            self.master = None
    def sendtopmost(self,event=None):
        self.master.lift()
        self.master.focus_force()
    def addcursor(self):
        iid = self.cursorlist.insert('','end',values=('',0,0,0))
        self.cursorlist.item(iid,text=iid)
        self.cursors[iid] = drawcursor.marker_simple(self,self.mainwindow.ax_height,self.mainwindow.fig_canvas,'g',self.mainwindow.sendtopmost,self.sendtopmost)
        temp = self.cursorlist.item(iid, 'values')
        self.cursorlist.item(iid,values=(self.edit_vals['Track'].get(),temp[1],temp[2],temp[3]))
        self.movecursor(iid_argv = iid)
        
    def movecursor(self,iid_argv=None):
        if iid_argv is None:
            iid = self.edit_vals['ID'].get()
        else:
            iid = iid_argv
        def abspos(x,y):
            temp = self.cursorlist.item(iid, 'values')
            self.cursorlist.item(iid,values=(temp[0],x,y,temp[3]))
            return (x,y)
        def trackpos(x,y,key):
            temp = self.cursorlist.item(iid, 'values')
            result = nearestpoint(x,y,key)
            self.cursorlist.item(iid,values=(temp[0],result[0],result[3],result[6]))
            return (result[0],result[3])
        def nearestpoint(x,y,track_key):
            inputpos = np.array([x,y])
            track_data_tmp = self.mainwindow.mainwindow.trackcontrol.track[track_key]['result']
            track_data = np.vstack((track_data_tmp[:,0],track_data_tmp[:,3])).T
            distance = (track_data - inputpos)**2
            min_dist_ix = np.argmin(np.sqrt(distance[:,0]+distance[:,1]))
            if '@' not in track_key:
                result = self.mainwindow.mainwindow.trackcontrol.track[track_key]['result'][min_dist_ix]
            elif '@OT_' in track_key:
                parent_tr = re.search('(?<=@OT_).+(?=@)',track_key).group(0)
                child_tr =  track_key.split('@_')[-1]
                result = self.mainwindow.mainwindow.trackcontrol.track[parent_tr]['othertrack'][child_tr]['result'][min_dist_ix]
            else:
                result = self.mainwindow.mainwindow.trackcontrol.pointsequence_track.track[track_key]['result'][min_dist_ix]
            return result
            
        def printpos(self_loc):
            print(iid, self_loc)

        trackkey = self.edit_vals['Track'].get()
        if trackkey == '@absolute':
            self.cursors[iid].start(lambda x,y: abspos(x,y), lambda self: printpos(self))
        else:
            self.cursors[iid].start(lambda x,y: trackpos(x,y,trackkey), lambda self: printpos(self))
        
    def deletecursor(self):
        selected = self.cursorlist.focus()
        if len(selected)>0:
            self.cursorlist.delete(selected)
            self.cursors[selected].deleteobj()
            del self.cursors[selected]
    def make_trackkeylist(self):
        currentval = self.edit_vals['Track'].get()

        owot_keys = []
        for parent_tr in self.mainwindow.mainwindow.trackcontrol.track.keys():
            for child_tr in self.mainwindow.mainwindow.trackcontrol.track[parent_tr]['othertrack'].keys():
                owot_keys.append('@OT_{:s}@_{:s}'.format(parent_tr,child_tr))

        self.edit_entries['Track']['values'] = tuple(['@absolute'])\
            +tuple(self.mainwindow.mainwindow.trackcontrol.track.keys())\
            +tuple(self.mainwindow.mainwindow.trackcontrol.pointsequence_track.track.keys())\
            +tuple(owot_keys)

        if currentval not in self.edit_entries['Track']['values']:
            self.edit_vals['Track'].set('@absolute')
    def reload_trackkeys(self):
        if self.master is not None:
            self.make_trackkeylist()
