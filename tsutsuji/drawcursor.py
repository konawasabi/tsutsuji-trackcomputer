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

import numpy as np

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
    def start(self):
        if self.pointerdir != None:
            self.pointerdir.remove()
            self.pointerdir = None
        self.track_key = self.p.values[3].get()
        self.pointed_pos = np.array([self.p.values[0].get(),self.p.values[1].get()])
        self.press_id = self.canvas.mpl_connect('button_press_event',self.press)
        self.move_id = self.canvas.mpl_connect('motion_notify_event',self.move)
    def move(self,event):
        position = np.array([event.xdata,event.ydata])
        if self.track_key == '@absolute':
            vector = (position - self.pointed_pos)
            element = vector/np.sqrt(vector[0]**2+vector[1]**2)
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
        self.canvas.draw()
        
        sin = vector[1]/np.sqrt(vector[0]**2+vector[1]**2)
        cos = vector[0]/np.sqrt(vector[0]**2+vector[1]**2)
        theta = np.arccos(cos) if sin > 0 else -np.arccos(cos)
        self.p.values[2].set(np.rad2deg(theta))
        self.p.parent.setdistance()
    def press(self,event):
        self.canvas.mpl_disconnect(self.press_id)
        self.canvas.mpl_disconnect(self.move_id)
    def setobj(self,element,reset=False):
        if self.pointerdir == None or reset:
            if reset:
                self.pointed_pos = np.array([self.p.values[0].get(),self.p.values[1].get()])
            self.pointerdir = self.ax.quiver(self.pointed_pos[0],self.pointed_pos[1],element[0],element[1],\
                                             angles='xy',scale=2,scale_units='inches',width=0.0025)
        else:
            self.pointerdir.set_UVC(element[0],element[1])