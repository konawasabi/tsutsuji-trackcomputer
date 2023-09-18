#
#    Copyright 2021-2023 konawasabi
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

import numpy as np
from . import math
import tkinter as tk
import re

from kobushi import dialog_multifields

class cursor():
    def __init__(self,parent):
        self.p = parent
    def point_and_dir(self):
        def click_1st(event):
            nonlocal pointed_pos,press2nd_id,motion_id
            pointerpos.set_data(event.xdata,event.ydata)
            pointed_pos = np.array([event.xdata,event.ydata])
            self.p.fig_canvas.draw()
            self.p.fig_canvas.mpl_disconnect(press1st_id)
            press2nd_id = self.p.fig_canvas.mpl_connect('button_press_event',click_2nd)
            motion_id = self.p.fig_canvas.mpl_connect('motion_notify_event',motion)
        def motion(event):
            nonlocal pointed_pos,press2nd_id,motion_id,pointerdir
            position = np.array([event.xdata,event.ydata])
            vector = (position - pointed_pos)
            vector = vector/np.sqrt(np.dot(vector,vector))
            if pointerdir == None:
                pointerdir = self.p.ax_plane.quiver(event.xdata,event.ydata,vector[0],vector[1],angles='xy',scale=2,scale_units='inches',width=0.0025)
            else:
                #pointerdir.set_data(event.xdata,event.ydata,vector[0],vector[1])
                pointerdir.set_UVC(vector[0],vector[1])
            self.p.fig_canvas.draw()
        def click_2nd(event):
            nonlocal press2nd_id,motion_id
            #print(press2nd_id,motion_id)
            self.p.fig_canvas.mpl_disconnect(press2nd_id)
            self.p.fig_canvas.mpl_disconnect(motion_id)
            self.p.drawall()
            print('Done')
        pointerpos, = self.p.ax_plane.plot([],[],'rx')
        pointerdir = None
        press1st_id = self.p.fig_canvas.mpl_connect('button_press_event',click_1st)
        press2nd_id = None
        motion_id = None
        pointed_pos = None
    def distance2pos(self):
        def click_1st(event):
            nonlocal pointerpos1,pointerpos2,pointed_pos,press1st_id,click_num
            if click_num == 0:
                pointerpos1.set_data(event.xdata,event.ydata)
                pointed_pos = np.array([event.xdata,event.ydata])
                self.p.fig_canvas.draw()
                print('data pos: ({:.2f},{:.2f})'.format(event.xdata,event.ydata))
                click_num +=1
            elif click_num == 1:
                pointerpos2.set_data(event.xdata,event.ydata)
                self.p.fig_canvas.draw()
                print('data pos: ({:.2f},{:.2f})'.format(event.xdata,event.ydata))
                print(np.sqrt((pointed_pos[0]-event.xdata)**2+(pointed_pos[1]-event.ydata)**2))
                click_num +=1
            else:
                self.p.fig_canvas.mpl_disconnect(press1st_id)
                self.p.drawall()
                print('Done')
        pointerpos1, = self.p.ax_plane.plot([],[],'rx')
        pointerpos2, = self.p.ax_plane.plot([],[],'bx')
        press1st_id = self.p.fig_canvas.mpl_connect('button_press_event',click_1st)
        pointed_pos = None
        click_num = 0

class marker():
    def __init__(self,parent,color):
        self.p = parent
        self.ax = self.p.parentwindow.ax_plane
        self.canvas = self.p.parentwindow.fig_canvas
        self.color = color

        self.setmarkerobj()
        self.prev_trackpos = None
    def start(self):
        self.track_key = self.p.values[3].get()
        if self.track_key != '@absolute':
            self.track_data = self.p.parent.mainwindow.trackcontrol.track[self.track_key]['result'][:,1:3]
        elif '@OWOT_' in self.track_key:
            parent_tr = re.search('(?<=@OWOT_).+(?=@)',self.track_key).group(0)
            child_tr =  self.track_key.split('@_')[-1]
            self.track_data = self.p.parent.mainwindow.trackcontrol.track[parent_tr]['othertrack'][child_tr]['result'][:,1:3]
        else:
            self.track_data = None

        self.press_id = self.canvas.mpl_connect('button_press_event',self.press)
        self.move_id = self.canvas.mpl_connect('motion_notify_event',self.move)
    def setpos(self,x,y):
        self.markerpos.set_data(x,y)
        self.p.values[0].set(x)
        self.p.values[1].set(y)
        self.p.parent.setdistance()
        self.canvas.draw()
    def move(self,event):
        xpos = event.xdata
        ypos = event.ydata
        if self.track_key == '@absolute':
            self.setpos(xpos,ypos)
        else:
            result = self.nearestpoint(xpos,ypos)
            self.setpos(result[1],result[2])
    def press(self,event):
        xpos = event.xdata
        ypos = event.ydata
        if self.track_key == '@absolute':
            self.setpos(xpos,ypos)
        else:
            result = self.nearestpoint(xpos,ypos)
            self.setpos(result[1],result[2])
            self.prev_trackpos = result
        self.canvas.mpl_disconnect(self.press_id)
        self.canvas.mpl_disconnect(self.move_id)
    def nearestpoint(self,x,y):
        inputpos = np.array([x,y])
        distance = (self.track_data - inputpos)**2
        min_dist_ix = np.argmin(np.sqrt(distance[:,0]+distance[:,1]))
        if '@OWOT_' in self.track_key:
            parent_tr = re.search('(?<=@OWOT_).+(?=@)',self.track_key).group(0)
            child_tr =  self.track_key.split('@_')[-1]
            return self.p.parent.mainwindow.trackcontrol.track[parent_tr]['othertrack'][child_tr]['result'][min_dist_ix]
        else:
            return self.p.parent.mainwindow.trackcontrol.track[self.track_key]['result'][min_dist_ix]
    def setmarkerobj(self,pos=False):
        self.markerpos, = self.ax.plot([],[],self.color+'x')
        if pos:
            self.markerpos.set_data(self.p.values[0].get(),self.p.values[1].get())
        
class arrow():
    def __init__(self,parent,marker):
        self.p = parent
        self.ax = self.p.parentwindow.ax_plane
        self.canvas = self.p.parentwindow.fig_canvas
        self.marker = marker
        
        self.pointerdir = None
        self.tangentline = None
        self.lastmousepoint = np.array([0, 0])
    def start(self):
        if self.pointerdir is not None:
            self.pointerdir.remove()
            self.pointerdir = None
        if self.tangentline is not None:
            self.tangentline.remove()
            self.tangentline = None
        self.track_key = self.p.values[3].get()
        self.pointed_pos = np.array([self.p.values[0].get(),self.p.values[1].get()])
        self.p.parentwindow.sendtopmost()
        self.press_id = self.canvas.mpl_connect('button_press_event',self.press)
        self.move_id = self.canvas.mpl_connect('motion_notify_event',self.move)
    def move(self,event):
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
    def press(self,event):
        self.p.parent.printdirection(mycursor=self.p)
        self.p.parent.sendtopmost()
        self.canvas.mpl_disconnect(self.press_id)
        self.canvas.mpl_disconnect(self.move_id)
    def setobj(self,element,reset=False):
        if self.pointerdir == None or reset:
            if reset:
                self.pointed_pos = np.array([self.p.values[0].get(),self.p.values[1].get()])
                element = (np.cos(np.deg2rad(self.p.values[2].get())),np.sin(np.deg2rad(self.p.values[2].get())))
            figsize = self.p.parentwindow.fig_plane.get_size_inches()
            self.pointerdir = self.ax.quiver(self.pointed_pos[0],self.pointed_pos[1],element[0],element[1],\
                                             angles='xy',scale=2,scale_units='inches',width=0.0025*7/figsize[0])
        else:
            self.pointerdir.set_UVC(element[0],element[1])
    def settangent(self,pointerpos,reset=False):
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
    def set_direct(self):
        if self.pointerdir != None:
            self.pointerdir.remove()
            self.pointerdir = None
        self.setobj(None,reset=True)
        #self.p.parent.printdirection()
        self.canvas.draw()

class marker_simple():
    def __init__(self,parent,ax,canvas,color,ch_main,ch_measure):
        self.parent = parent
        self.ax = ax
        self.canvas = canvas
        self.color = color
        self.ch_main = ch_main
        self.ch_measure = ch_measure

        self.setobj()
    def start(self,posfunc,pressfunc):
        self.posfunc = posfunc
        self.pressfunc = pressfunc
        self.ch_main()
        self.press_id = self.canvas.mpl_connect('button_press_event',self.press)
        self.move_id = self.canvas.mpl_connect('motion_notify_event',self.move)
    def move(self,event):
        if event.xdata is not None and event.ydata is not None:
            self.setpos(event.xdata,event.ydata)
    def press(self,event):
        if event.xdata is not None and event.ydata is not None:
            self.setpos(event.xdata,event.ydata)
        self.pressfunc(self)
        self.ch_measure()
        self.canvas.mpl_disconnect(self.press_id)
        self.canvas.mpl_disconnect(self.move_id)
    def setpos(self,x,y,direct=False):
        if direct:
            self.xout = x
            self.yout = y
        else:
            self.xout, self.yout = self.posfunc(x,y)
        self.markerpos.set_data(self.xout,self.yout)
        #self.annotate.set(text ='({:.1f},{:.1f})'.format(self.xout,self.yout), position=(self.xout,self.yout))
        self.canvas.draw()
    def setobj(self):
        self.markerpos, = self.ax.plot([],[],self.color+'x')
        #self.annotate = self.ax.text(0,0,'')

class marker_pos():
    def __init__(self,parent,color):
        self.p = parent
        self.ax = self.p.parentwindow.ax_plane
        self.canvas = self.p.parentwindow.fig_canvas
        self.color = color

        self.markerobj = marker_simple(self.p,self.ax,self.canvas,self.color,self.p.parentwindow.sendtopmost,self.p.parent.sendtopmost)
        self.markerobj.posfunc = lambda x,y:self.posfunc(x,y)
        self.markerobj.pressfunc = lambda p:self.pressfunc(p)
    def start(self):
        self.track_key = self.p.values[3].get()
        if '@' not in self.track_key:
            self.track_data = self.p.parent.mainwindow.trackcontrol.track[self.track_key]['result'][:,1:3]
        elif '@OT_' in self.track_key:
            parent_tr = re.search('(?<=@OT_).+(?=@)',self.track_key).group(0)
            child_tr =  self.track_key.split('@_')[-1]
            self.track_data = self.p.parent.mainwindow.trackcontrol.track[parent_tr]['othertrack'][child_tr]['result'][:,1:3]
        elif '@KML_' in self.track_key or '@CSV_' in self.track_key:
            self.track_data = self.p.parent.mainwindow.trackcontrol.pointsequence_track.track[self.track_key]['result'][:,1:3]
        else:
            self.track_data = None
        self.markerobj.start(lambda x,y:self.posfunc(x,y),lambda p:self.pressfunc(p))
    def move(self,event):
        self.markerobj.move(event)
    def press(self,event):
        self.markerobj.press(event)
    def nearestpoint(self,x,y):
        inputpos = np.array([x,y])
        distance = (self.track_data - inputpos)**2
        min_dist_ix = np.argmin(np.sqrt(distance[:,0]+distance[:,1]))
        if '@' not in self.track_key:
            result = self.p.parent.mainwindow.trackcontrol.track[self.track_key]['result'][min_dist_ix]
        elif '@OT_' in self.track_key:
            parent_tr = re.search('(?<=@OT_).+(?=@)',self.track_key).group(0)
            child_tr =  self.track_key.split('@_')[-1]
            result = self.p.parent.mainwindow.trackcontrol.track[parent_tr]['othertrack'][child_tr]['result'][min_dist_ix]
        else:
            result = self.p.parent.mainwindow.trackcontrol.pointsequence_track.track[self.track_key]['result'][min_dist_ix]
        return result
    def setmarkerobj(self,pos=False):
        self.markerobj.setobj()
        if pos:
            #self.markerobj.setpos(self.p.values[0].get(),self.p.values[1].get())
            self.set_direct(replot=True)
    def posfunc(self,xpos,ypos):
        if self.track_key == '@absolute':
            x = xpos
            y = ypos
            kp = None
        else:
            result = self.nearestpoint(xpos,ypos)
            x = result[1]
            y = result[2]
            kp = result[0]
        self.p.values[0].set(x)
        self.p.values[1].set(y)
        self.p.values_toshow[0].set('{:.3f}'.format(x))
        self.p.values_toshow[1].set('{:.3f}'.format(y))
        if kp is not None:
            self.p.values[4].set(kp)
            self.p.values_toshow[4].set('{:.3f}'.format(kp))
        self.p.parent.setdistance()
        return x,y
    def pressfunc(self,parent):
        self.p.parent.printdistance(mycursor=self.p)
        if self.track_key != '@absolute':
            self.prev_trackpos = self.nearestpoint(self.markerobj.xout,self.markerobj.yout)
    def set_direct(self,replot=False):
        self.track_key = self.p.values[3].get()
        if self.track_key == '@absolute':
            self.track_data = None
            kp = None
        else:
            kp = self.p.values[4].get()
            if '@' not in self.track_key:
                self.track_data = self.p.parent.mainwindow.trackcontrol.track[self.track_key]['result']
            elif '@OT_' in self.track_key:
                parent_tr = re.search('(?<=@OT_).+(?=@)',self.track_key).group(0)
                child_tr =  self.track_key.split('@_')[-1]
                self.track_data = self.p.parent.mainwindow.trackcontrol.track[parent_tr]['othertrack'][child_tr]['result']
            else:
                self.track_data = self.p.parent.mainwindow.trackcontrol.pointsequence_track.track[self.track_key]['result']

            pos_kp = []
            for i in range(0,5):
                if '@' not in self.track_key:
                    pos_kp.append(math.interpolate_with_dist(self.p.parent.mainwindow.trackcontrol.track[self.track_key]['result'],i,kp))
                elif '@OT_' in self.track_key:
                    parent_tr = re.search('(?<=@OT_).+(?=@)',self.track_key).group(0)
                    child_tr =  self.track_key.split('@_')[-1]
                    pos_kp.append(math.interpolate_with_dist(self.p.parent.mainwindow.trackcontrol.track[parent_tr]['othertrack'][child_tr]['result'],i,kp))
                else:
                    pos_kp.append(math.interpolate_with_dist(self.p.parent.mainwindow.trackcontrol.pointsequence_track.track[self.track_key]['result'],i,kp))
            #pos_kp = self.track_data[self.track_data[:,0] == kp][-1]
           
            if self.p.coordinate_v.get() == 'abs':
                offset = np.array([0,0])
                offs_angle = 0 
            else:
                offset_input =dialog_multifields.dialog_multifields(self.p.parent.mainwindow,\
                                                      [{'name':'x', 'type':'Double', 'label':'x','default':0},\
                                                       {'name':'y', 'type':'Double', 'label':'y','default':0},\
                                                       {'name':'theta', 'type':'Double', 'label':'theta','default':0}],\
                                                      message = 'set offset')
                offs_angle =np.deg2rad(float(offset_input.variables['theta'].get()))
                offset = np.dot(math.rotate(pos_kp[4]+offs_angle), np.array([float(offset_input.variables['x'].get()), float(offset_input.variables['y'].get())]))
                

            self.p.values[0].set(pos_kp[1]+offset[0])
            self.p.values[1].set(pos_kp[2]+offset[1])
            self.p.values_toshow[0].set('{:.1f}'.format(pos_kp[1]+offset[0]))
            self.p.values_toshow[1].set('{:.1f}'.format(pos_kp[2]+offset[1]))

            self.p.values[2].set(np.rad2deg(pos_kp[4]+offs_angle))
            self.p.values_toshow[2].set('{:.1f}'.format(np.rad2deg(pos_kp[4]+offs_angle)))

            self.prev_trackpos = pos_kp
            if '@' not in self.track_key:
                self.track_data = self.p.parent.mainwindow.trackcontrol.track[self.track_key]['result'][:1,3]
            elif '@OT_' in self.track_key:
                parent_tr = re.search('(?<=@OT_).+(?=@)',self.track_key).group(0)
                child_tr =  self.track_key.split('@_')[-1]
                self.track_data = self.p.parent.mainwindow.trackcontrol.track[parent_tr]['othertrack'][child_tr]['result'][:1,3]
            else:
                self.track_data = self.p.parent.mainwindow.trackcontrol.pointsequence_track.track[self.track_key]['result'][:1,3]

            if self.p.coordinate_v.get() != 'abs':
                self.track_key = '@absolute'
                self.p.values[3].set('@absolute')
                self.p.coordinate_v.set('abs')
                
        self.markerobj.setpos(self.p.values[0].get(),self.p.values[1].get(),direct=True)
        if not replot:
            self.p.parent.setdistance()
            #self.p.parent.printdistance()
