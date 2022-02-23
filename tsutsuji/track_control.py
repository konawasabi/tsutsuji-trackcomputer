'''
    Copyright 2021-2022 konawasabi

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

from kobushi import mapinterpreter
from kobushi import trackgenerator

from . import config
from . import math

class TrackControl():
    def __init__(self):
        self.track = {}
        self.rel_track = {}
        self.rel_track_radius = {}
        self.rel_track_radius_cp = {}
        self.conf = None
    def loadcfg(self,path):
        self.conf = config.Config(path)
    def loadmap(self,to_load=None):
        if self.conf != None:
            for i in self.conf.track_keys:
                self.track[i] = {}
                self.track[i]['interp'] = mapinterpreter.ParseMap(env=None,parser=None)
                self.track[i]['data'] = self.track[i]['interp'].load_files(self.conf.track_data[i]['file'])
                self.track[i]['data'].cp_arbdistribution = [min(self.track[i]['data'].controlpoints.list_cp),\
                                                            self.conf.track_data[i]['endpoint'],\
                                                            self.conf.general['unit_length']]
                self.track[i]['tgen'] = trackgenerator.TrackGenerator(self.track[i]['data'],\
                                                                x0 = self.conf.track_data[i]['z'],\
                                                                y0 = self.conf.track_data[i]['x'],\
                                                                z0 = self.conf.track_data[i]['y'],\
                                                                theta0 = self.conf.track_data[i]['angle'])
                self.track[i]['result'] = self.track[i]['tgen'].generate_owntrack()
    def relativepoint(self,to_calc=None):
        calc_track = [i for i in self.conf.track_keys if i != self.conf.owntrack] if to_calc == None else to_calc
        for tr in calc_track:
            tgt = self.track[tr]['result']
            src = self.track[self.conf.owntrack]['result']
            self.rel_track[tr] = []
            len_tr = len(tgt)
            # 自軌道に対する相対座標の算出
            for pos in src:
                tgt_xy = np.vstack((tgt[:,1],tgt[:,2]))
                tgt_xy_trans = np.dot(math.rotate(-pos[4]),(tgt_xy - np.vstack((pos[1],pos[2])) ) ) # 自軌道注目点を原点として座標変換
                min_ix = np.where(np.abs(tgt_xy_trans[0])==min(np.abs(tgt_xy_trans[0]))) # 変換後の座標でx'成分絶対値が最小となる点(=y'軸との交点)のインデックスを求める
                min_ix_val = min_ix[0][0]
                
                if min_ix_val > 0 and min_ix_val < len_tr-1: # y'軸との最近接点が軌道区間内にある場合
                    aroundzero = np.vstack((tgt_xy_trans[0][min_ix_val-1:min_ix_val+2],tgt_xy_trans[1][min_ix_val-1:min_ix_val+2]))
                    signx = np.sign(aroundzero[0])
                    if signx[0] != signx[1]:
                        y0 = (aroundzero[1][1]-aroundzero[1][0])/(aroundzero[0][1]-aroundzero[0][0])*(-aroundzero[0][0])+aroundzero[1][0]
                        self.rel_track[tr].append([pos[0], 0,y0])
                    elif signx[1] != signx[2]:
                        y0 = (aroundzero[1][2]-aroundzero[1][1])/(aroundzero[0][2]-aroundzero[0][1])*(-aroundzero[0][1])+aroundzero[1][1]
                        self.rel_track[tr].append([pos[0], 0,y0])
                else:
                    self.rel_track[tr].append([pos[0], tgt_xy_trans[0][min_ix][0],tgt_xy_trans[1][min_ix][0]]) # y'軸との交点での自軌道距離程、x'成分(0になるべき)、y'成分(相対距離)を出力
            self.rel_track[tr]=np.array(self.rel_track[tr])
    def relativeradius(self,to_calc=None):
        calc_track = [i for i in self.conf.track_keys if i != self.conf.owntrack] if to_calc == None else to_calc
        for tr in calc_track:
            self.rel_track_radius[tr] = []
            # 相対曲率半径の算出
            for ix in range(0,len(self.rel_track[tr])-2):
                pos = []
                pos.append(self.rel_track[tr][ix])
                pos.append(self.rel_track[tr][ix+1])
                pos.append(self.rel_track[tr][ix+2])
                
                ds = np.sqrt((pos[1][0]-pos[0][0])**2 + (pos[1][2]-pos[0][2])**2)
                dalpha = np.arctan((pos[2][2]-pos[1][2])/(pos[2][0]-pos[1][0])) - np.arctan((pos[1][2]-pos[0][2])/(pos[1][0]-pos[0][0]))
                curvature = dalpha/ds
                self.rel_track_radius[tr].append([pos[0][0],curvature,1/curvature if np.abs(1/curvature) < 1e4 else 0])
                
            self.rel_track_radius[tr]=np.array(self.rel_track_radius[tr])
    def relativeradius_cp(self,to_calc=None):
        calc_track = [i for i in self.conf.track_keys if i != self.conf.owntrack] if to_calc == None else to_calc
        cp_dist = []
        for dat in self.track[self.conf.owntrack]['data'].own_track.data:
            cp_dist.append(dat['distance'])
        cp_dist = sorted(set(cp_dist))
        for tr in calc_track:
            self.rel_track_radius_cp[tr] = []
            
            #pos_cp = self.track[key]['result'][np.isin(self.track[key]['result'][:,0],cp_dist)]

            ix=0
            while ix < len(cp_dist)-1:
                pos_cp = self.rel_track_radius[tr][(self.rel_track_radius[tr][:,0]>=cp_dist[ix]) & (self.rel_track_radius[tr][:,0]<cp_dist[ix+1])]
                len_section = cp_dist[ix+1] - cp_dist[ix]
                curvature_section = np.sum(pos_cp[:,1])/len_section
                yval = self.rel_track[tr][self.rel_track[tr][:,0] == cp_dist[ix]][0][2]
                self.rel_track_radius_cp[tr].append([cp_dist[ix],curvature_section,1/curvature_section if np.abs(1/curvature_section) < 1e4 else 0,yval])
                ix+=1
            self.rel_track_radius_cp[tr] = np.array(self.rel_track_radius_cp[tr])
            #print(self.rel_track_radius[tr])
            print(self.rel_track_radius_cp[tr])
    def plot2d(self, ax):
        if len(self.track) > 0:
            for i in self.conf.track_keys:
                tmp = self.track[i]['result']
                ax.plot(tmp[:,1],tmp[:,2],label=i)
            #ax.invert_yaxis()
            #ax.set_aspect('equal')
    def drawarea(self, extent_input = None):
        extent = [0,0,0,0] if extent_input == None else extent_input
        if len(self.track) > 0:
            for i in self.conf.track_keys:
                tmp_src = self.track[i]['result']
                tmp_result = [min(tmp_src[:,1]),max(tmp_src[:,1]),min(tmp_src[:,2]),max(tmp_src[:,2])]
                extent[0] = tmp_result[0] if tmp_result[0] < extent[0] else extent[0]
                extent[1] = tmp_result[1] if tmp_result[1] > extent[1] else extent[1]
                extent[2] = tmp_result[2] if tmp_result[2] < extent[2] else extent[2]
                extent[3] = tmp_result[3] if tmp_result[3] > extent[3] else extent[3]
        return extent
    def dump_trackdata(self):
        for key in self.conf.track_keys:
            #print(key)
            for type in ['radius','cant','interpolate_func','center','gauge','turn','gradient']:
                print(key,type)
                for dat in self.track[key]['data'].own_track.data:
                    if dat['key'] == type:
                        print(dat)
            print()
    def dump_trackpos(self):
        for key in self.conf.track_keys:
            print(key)
            print(self.track[key]['result'])
    def plot_controlpoints(self,ax):
        for key in self.conf.track_keys:
            cp_dist = []
            for dat in self.track[key]['data'].own_track.data:
                cp_dist.append(dat['distance'])
            cp_dist = sorted(set(cp_dist))
            pos_cp = self.track[key]['result'][np.isin(self.track[key]['result'][:,0],cp_dist)]
            print(key)
            print(cp_dist)
            ax.scatter(pos_cp[:,1],pos_cp[:,2])
            if(key != 'down'):
                target = self.track['down']['result'][:,1:3]
                kp_cp = []
                rel_dist = []
                for data in pos_cp:
                    inputpos = np.array([data[1],data[2]])
                    result = math.minimumdist(target,inputpos)
                    kp_cp.append(math.cross_kilopost(self.track['down']['result'],result))
                    rel_dist.append(result[0])
                    ax.plot([inputpos[0],result[1][0]],[inputpos[1],result[1][1]],color='black')
                print(kp_cp)
                print(rel_dist)
