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
import re
import itertools

from kobushi import trackcoordinate

from . import drawcursor
from . import math

'''
from . import solver
from . import curvetrackplot
'''

class arrow():
    def __init__(self,parent,marker,figure):
        self.p = parent
        self.marker = marker
        self.ax = self.marker.ax
        self.canvas = self.marker.canvas
        self.ch_main = self.marker.ch_main
        self.ch_measure = self.marker.ch_measure
        self.figure = figure
        
        self.pointerdir = None
        self.tangentline = None
        self.lastmousepoint = np.array([0, 0])
        self.pointed_pos = np.array([0,0])
    def __del__(self):
        pass
    def start(self,posfunc,pressfunc,x,y):
        self.posfunc = posfunc
        self.pressfunc = pressfunc

        self.ch_main()
        self.deleteobj()
        self.press_id = self.canvas.mpl_connect('button_press_event',self.press)
        self.move_id = self.canvas.mpl_connect('motion_notify_event',self.move)

        self.pointed_pos = np.array([x,y])

        '''
        self.track_key = self.p.values[3].get()
        self.pointed_pos = np.array([self.p.values[0].get(),self.p.values[1].get()])
        self.p.parentwindow.sendtopmost()
        '''
    def move(self,event):
        if event.xdata is not None and event.ydata is not None:
            self.setpos(event.xdata,event.ydata)
        '''
        position = np.array([event.xdata,event.ydata])
        if event.xdata is not None and event.ydata is not None:
            if self.track_key == '@absolute':
                vector = (position - self.pointed_pos)
                element = vector/np.sqrt(vector[0]**2+vector[1]**2)
                self.lastmousepoint = np.array([event.xdata, event.ydata])
            else:
                v_marker = (position - self.pointed_pos)
                v_track = np.array([np.cos(self.marker.prev_trackpos[4]),np.sin(self.marker.prev_trackpos[4])])
                if np.dot(v_marker, v_track) > 0:
                    vector = v_track
                    element = vector
                else:
                    vector = np.array([np.cos(self.marker.prev_trackpos[4]-np.pi),np.sin(self.marker.prev_trackpos[4]-np.pi)])
                    element = vector
            self.setobj(element)
            if self.track_key == '@absolute':
                self.settangent(position)
            self.canvas.draw()

            sin = vector[1]/np.sqrt(vector[0]**2+vector[1]**2)
            cos = vector[0]/np.sqrt(vector[0]**2+vector[1]**2)
            theta = np.arccos(cos) if sin > 0 else -np.arccos(cos)
            self.p.values[2].set(np.rad2deg(theta))
            self.p.values_toshow[2].set('{:.3f}'.format(np.rad2deg(theta)))
            self.p.parent.setdistance()
        '''
    def press(self,event):
        #if event.xdata is not None and event.ydata is not None:
        #    self.setpos(event.xdata,event.ydata)
        self.pressfunc(self)
        self.ch_measure()
        self.canvas.mpl_disconnect(self.press_id)
        self.canvas.mpl_disconnect(self.move_id)
    def setpos(self, x, y, direct=False):
        position = np.array([x,y])
        vector = (position - self.pointed_pos)
        element = vector/np.sqrt(vector[0]**2+vector[1]**2)
        self.lastmousepoint = np.array([x, y])
        self.setobj(element)
        self.settangent(position,self.pointed_pos)
        self.canvas.draw()
    def setobj(self,element,reset=False):
        if self.pointerdir == None or reset:
            if reset:
                #self.pointed_pos = np.array([self.p.values[0].get(),self.p.values[1].get()])
                #element = (np.cos(np.deg2rad(self.p.values[2].get())),np.sin(np.deg2rad(self.p.values[2].get())))
                marker_pos = self.marker.markerpos.get_lines()[0].get_data()
                self.pointed_pos = np.array([marker_pos[0][0],marker_pos[1][0]])
                element = (1,0)
            figsize = self.figure.get_size_inches()
            self.pointerdir = self.ax.quiver(self.pointed_pos[0],self.pointed_pos[1],element[0],element[1],\
                                             angles='xy',scale=2,scale_units='inches',width=0.0025*7/figsize[0])
        else:
            self.pointerdir.set_UVC(element[0],element[1])
    def settangent(self,pointerpos,origin,reset=False):
        '''
        if self.p.values[3].get() == '@absolute':
            if reset:
                pointerpos = self.lastmousepoint
            origin = np.array([self.p.values[0].get(),self.p.values[1].get()])
            diff = pointerpos - origin
            diagonal = np.dot(math.rotate(np.pi),diff) + origin

            if self.tangentline == None or reset:
                self.tangentline, = self.ax.plot([diagonal[0],pointerpos[0]],[diagonal[1],pointerpos[1]],'k--',alpha=0.25)
            else:
                self.tangentline.set_data([diagonal[0],pointerpos[0]],[diagonal[1],pointerpos[1]])
        '''
        if reset:
            pointerpos = self.lastmousepoint
        diff = pointerpos - origin
        diagonal = np.dot(math.rotate(np.pi),diff) + origin

        if self.tangentline == None or reset:
            self.tangentline, = self.ax.plot([diagonal[0],pointerpos[0]],[diagonal[1],pointerpos[1]],'k--',alpha=0.25)
        else:
            self.tangentline.set_data([diagonal[0],pointerpos[0]],[diagonal[1],pointerpos[1]])
    def set_direct(self):
        if self.pointerdir != None:
            self.pointerdir.remove()
            self.pointerdir = None
        self.setobj(None,reset=True)
        #self.p.parent.printdirection()
        self.canvas.draw()
    def deleteobj(self):
        if self.pointerdir is not None:
            self.pointerdir.remove()
            self.pointerdir = None
        if self.tangentline is not None:
            self.tangentline.remove()
            self.tangentline = None
        self.canvas.draw()
        

class Interface():
    class unitCursor(drawcursor.marker_simple):
        def __init__(self,parent,ax,canvas,color,ch_main,ch_measure,iid,figure):
            self.marker = None
            self.arrow = None
            self.makeobj(parent,ax,canvas,color,ch_main,ch_measure,figure)
            self.iid = iid
            self.values = {'Track':'', 'Distance':0, 'Height':0,'Gradient':0, 'Color':color}
        def makeobj(self,parent,ax,canvas,color,ch_main,ch_measure,figure):
            self.marker = drawcursor.marker_simple(parent,ax,canvas,color,ch_main,ch_measure)
            self.arrow = arrow(parent,self.marker,figure)
        def set_value(self,key,val):
            self.values[key] = val
        def get_value(self,key):
            return self.values[key]
        def start(self,posfunc,pressfunc):
            self.marker.start(posfunc,pressfunc)
        def move(self,event):
            self.marker.move(event)
        def press(self,event):
            self.marker.press(event)
        def setpos(self,x,y,direct=False):
            self.marker.setpos(x,y,direct)
        def setobj(self):
            self.marker.setobj()
        def deleteobj(self):
            self.marker.deleteobj()
            self.arrow.deleteobj()
        def setcolor(self,color):
            self.marker.setcolor(color)
        def start_arrow(self,posfunc,pressfunc):
            self.arrow.start(posfunc,pressfunc)
    def __init__(self,mainwindow):
        self.mainwindow = mainwindow
        self.master = None
        #self.trackcontrol = self.mainwindow.trackcontrol
        self.cursorlist_column = ('Track', 'Distance', 'Height', 'Gradient', 'Color')
        self.cursors = {}
        self.cursorcolors = itertools.cycle(['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd','#8c564b','#e377c2','#7f7f7f','#bcbd22','#17becf'])
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

            if len(self.cursors)>0:
                for key in self.cursors.keys():
                    self.resumecursor(key)
        else:
            self.sendtopmost()
    def create_widgets(self):
        self.cursorlist = ttk.Treeview(self.mainframe, column=self.cursorlist_column,height=5)
        self.cursorlist.bind('<<TreeviewSelect>>',self.click_cursorlist)
        self.cursorlist.column('#0',width=40)
        self.cursorlist.column('Track',width=100)
        self.cursorlist.column('Distance',width=80)
        self.cursorlist.column('Height',width=80)
        self.cursorlist.column('Gradient',width=80)
        self.cursorlist.column('Color',width=80)
        self.cursorlist.heading('#0',text='ID')
        self.cursorlist.heading('Track',text='Track')
        self.cursorlist.heading('Distance',text='Distance')
        self.cursorlist.heading('Height',text='Height')
        self.cursorlist.heading('Gradient',text='Gradient')
        self.cursorlist.heading('Color',text='Color')
        
        self.cursorlist.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

        self.edit_frame = ttk.Frame(self.mainframe, padding='3 3 3 3')
        self.edit_frame.grid(column=0, row=1,sticky=(tk.E, tk.W))

        edit_vals = ('ID', 'Track', 'Distance', 'Height', 'Gradient', 'Color')
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

        i = 'Color'
        self.edit_vals[i] = tk.StringVar(value='')
        self.edit_entries[i] = ttk.Entry(self.edit_frame, textvariable = self.edit_vals[i],width=10)
        self.edit_entries[i].bind('<Button-1>',self.choosecursorcolor)

        j = 0
        for i in edit_vals:
            self.edit_labels[i].grid(column=j, row=0,sticky=(tk.E, tk.W))
            self.edit_entries[i].grid(column=j, row=1,sticky=(tk.E, tk.W))
            j+=1

        self.button_frame = ttk.Frame(self.mainframe, padding='3 3 3 3')
        self.button_frame.grid(column=0, row=2,sticky=(tk.E, tk.W))

        self.add_b = ttk.Button(self.button_frame, text='Add', command=self.addcursor)
        self.edit_b = ttk.Button(self.button_frame, text='Edit', command=self.editcursor)
        self.move_b = ttk.Button(self.button_frame, text='Grad.', command=self.movearrow)
        self.del_b = ttk.Button(self.button_frame, text='Delete', command=self.deletecursor)

        self.add_b.grid(column=0, row=0,sticky=(tk.N, tk.E, tk.W))
        self.edit_b.grid(column=1, row=0,sticky=(tk.N, tk.E, tk.W))
        self.move_b.grid(column=2, row=0,sticky=(tk.N, tk.E, tk.W))
        self.del_b.grid(column=3, row=0,sticky=(tk.N, tk.E, tk.W))
        
    def closewindow(self):
        if self.master is not None:
            self.master.withdraw()
            self.master = None
    def sendtopmost(self,event=None):
        self.master.lift()
        self.master.focus_force()
    def addcursor(self):
        iid = self.cursorlist.insert('','end',values=('',0,0,0,''))
        self.cursorlist.item(iid,text=iid)
        color_temp = next(self.cursorcolors)
        self.cursors[iid] = self.unitCursor(self,self.mainwindow.ax_height,self.mainwindow.fig_canvas,color_temp,self.mainwindow.sendtopmost,self.sendtopmost,iid,self.mainwindow.fig_height)
        self.setcursorvalue(iid,'Track',self.edit_vals['Track'].get())
        self.setcursorvalue(iid,'Color',color_temp)
        self.movecursor(iid_argv = iid)
    def setcursorvalue(self,iid,key,value):
        self.cursors[iid].set_value(key,value)
        temp = self.cursorlist.item(iid, 'values')
        result = []
        for i in range(len(self.cursorlist_column)):
            if key == self.cursorlist_column[i]:
                result.append(value)
            else:
                result.append(temp[i])
        self.cursorlist.item(iid,values=(result))
    def movecursor(self,iid_argv=None):
        if iid_argv is None:
            iid = self.edit_vals['ID'].get()
        else:
            iid = iid_argv
        def abspos(x,y):
            self.setcursorvalue(iid,'Distance',x)
            self.setcursorvalue(iid,'Height',y)
            return (x,y)
        def trackpos(x,y,key):
            result = nearestpoint(x,y,key)
            self.setcursorvalue(iid,'Distance',result[0])
            self.setcursorvalue(iid,'Height',result[3])
            self.setcursorvalue(iid,'Gradient',result[6])
            return (result[0],result[3])
        def nearestpoint(x,y,track_key):
            inputpos = np.array([x,y])
            if '@' not in track_key:
                track_data_tmp = self.mainwindow.mainwindow.trackcontrol.track[track_key]['result']
            elif '@OT_' in track_key:
                parent_tr = re.search('(?<=@OT_).+(?=@)',track_key).group(0)
                child_tr =  track_key.split('@_')[-1]
                track_data_tmp = self.mainwindow.mainwindow.trackcontrol.track[parent_tr]['othertrack'][child_tr]['result']
            elif '@KML_' in track_key or '@CSV_' in track_key:
                track_data_tmp = self.mainwindow.mainwindow.trackcontrol.pointsequence_track.track[track_key]['result']
                
            
            track_data = np.vstack((track_data_tmp[:,0],track_data_tmp[:,3])).T
            distance = (track_data - inputpos)**2
            min_dist_ix = np.argmin(np.sqrt(distance[:,0]+distance[:,1]))
            result = track_data_tmp[min_dist_ix]
            return result
            
        def printpos(self_loc):
            print(iid, self_loc)
        def click():
            self.cursors[iid].arrow.start()

        trackkey = self.edit_vals['Track'].get()
        if trackkey == '@absolute':
            self.cursors[iid].marker.start(lambda x,y: abspos(x,y), lambda self: printpos(self))
        else:
            self.cursors[iid].marker.start(lambda x,y: trackpos(x,y,trackkey), lambda self: printpos(self))
    def deletecursor(self):
        selected = self.cursorlist.focus()
        if len(selected)>0:
            self.cursorlist.delete(selected)
            self.cursors[selected].deleteobj()
            del self.cursors[selected]
    def resumecursor(self,iid):
        self.cursorlist.insert('','end',iid=iid,text=iid,\
                               values=(self.cursors[iid].get_value('Track'),\
                                       self.cursors[iid].get_value('Distance'),\
                                       self.cursors[iid].get_value('Height'),\
                                       self.cursors[iid].get_value('Gradient'),\
                                       self.cursors[iid].get_value('Color')))
        self.cursors[iid].makeobj(self,\
                                  self.mainwindow.ax_height,\
                                  self.mainwindow.fig_canvas,\
                                  self.cursors[iid].get_value('Color'),\
                                  self.mainwindow.sendtopmost,\
                                  self.sendtopmost)
        self.cursors[iid].setobj()
        self.cursors[iid].setpos(self.cursors[iid].get_value('Distance'),self.cursors[iid].get_value('Height'),direct=True)
    def editcursor(self,iid=None):
        if iid is None:
            iid = self.edit_vals['ID'].get()

        if iid == '':
            return None
        key = 'Track'
        track_key = self.edit_vals[key].get()
        self.cursors[iid].set_value(key, track_key)
        self.setcursorvalue(iid,key,track_key)
        
        key = 'Distance'
        dist = self.edit_vals[key].get()
        
        if track_key == '@absolute':
            height = self.edit_vals['Height'].get()
            gradient = self.edit_vals['Gradient'].get()
        else:
            inputpos = np.array([dist,0])
            if '@' not in track_key:
                track_data_tmp = self.mainwindow.mainwindow.trackcontrol.track[track_key]['result']
            elif '@OT_' in track_key:
                parent_tr = re.search('(?<=@OT_).+(?=@)',track_key).group(0)
                child_tr =  track_key.split('@_')[-1]
                track_data_tmp = self.mainwindow.mainwindow.trackcontrol.track[parent_tr]['othertrack'][child_tr]['result']
            elif '@KML_' in track_key or '@CSV_' in track_key:
                track_data_tmp = self.mainwindow.mainwindow.trackcontrol.pointsequence_track.track[track_key]['result']
            track_data = np.vstack((track_data_tmp[:,0],track_data_tmp[:,3])).T
            distance = (track_data - inputpos)**2
            min_dist_ix = np.argmin(np.sqrt(distance[:,0]+distance[:,1]))
            result = track_data_tmp[min_dist_ix]
            dist = result[0]
            height = result[3]
            gradient = result[6]

        key = 'Distance'
        self.cursors[iid].set_value(key, dist)
        self.setcursorvalue(iid,key,dist)
        key = 'Height'
        self.cursors[iid].set_value(key, height)
        self.setcursorvalue(iid,key,height)
        key = 'Gradient'
        self.cursors[iid].set_value(key, gradient)
        self.setcursorvalue(iid,key,gradient)

        self.cursors[iid].setpos(dist,\
                                 height,direct=True)

        key = 'Color'
        self.cursors[iid].set_value(key, self.edit_vals[key].get())
        self.setcursorvalue(iid,key,self.edit_vals[key].get())
        self.cursors[iid].setcolor(self.edit_vals[key].get())
        
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
    def click_cursorlist(self, event=None):
        if event != None:
            selected = self.cursorlist.focus()
            if len(selected)>0:
                data = self.cursorlist.item(selected, 'values')
                self.edit_vals['ID'].set(selected)
                self.edit_vals['Track'].set(data[0])
                self.edit_vals['Distance'].set(data[1])
                self.edit_vals['Height'].set(data[2])
                self.edit_vals['Gradient'].set(data[3])
                self.edit_vals['Color'].set(data[4])
    def replotCursors(self):
        for key in self.cursors.keys():
            data = self.cursorlist.item(key,'values')
            self.cursors[key].setobj()
            self.cursors[key].setpos(float(data[1]),float(data[2]),direct=True)
        self.mainwindow.fig_canvas.draw()
    def choosecursorcolor(self,event=None):
        inputdata = colorchooser.askcolor(color=self.edit_vals['Color'].get())
        if inputdata[1] is not None:
            self.edit_vals['Color'].set(inputdata[1])
    def movearrow(self,iid_argv=None):
        if iid_argv is None:
            iid = self.edit_vals['ID'].get()
        else:
            iid = iid_argv
        marker_dist = self.cursors[iid].get_value('Distance')
        marker_height = self.cursors[iid].get_value('Height')
        self.cursors[iid].arrow.start(lambda x,y: (x,y),lambda x: print('end'),marker_dist, marker_height)
