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

from kobushi import mapinterpreter
from kobushi import trackgenerator

from . import config

class TrackControl():
    def __init__(self):
        self.track = {}
        self.rel_track = {}
        self.rel_track_radius = {}
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
            self.rel_track_radius[tr] = []
            len_tr = len(tgt)
            # 自軌道に対する相対座標の算出
            for pos in src:
                tgt_xy = np.vstack((tgt[:,1],tgt[:,2]))
                tgt_xy_trans = np.dot(self.rotate(-pos[4]),(tgt_xy - np.vstack((pos[1],pos[2])) ) ) # 自軌道注目点を原点として座標変換
                min_ix = np.where(np.abs(tgt_xy_trans[0])==min(np.abs(tgt_xy_trans[0]))) # 変換後の座標でx'成分絶対値が最小となる点(=y'軸との交点)のインデックスを求める
                min_ix_val = min_ix[0][0]
                
                if min_ix_val > 0 and min_ix_val < len_tr-1:
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
            
            # 相対曲率半径の算出
            for ix in range(0,len(rel_track[tr])-2):
                pos = []
                pos.append(rel_track[tr][ix])
                pos.append(rel_track[tr][ix+1])
                pos.append(rel_track[tr][ix+2])
                
                ds = np.sqrt((pos[1][0]-pos[0][0])**2 + (pos[1][2]-pos[0][2])**2)
                dalpha = np.arctan((pos[2][2]-pos[1][2])/(pos[2][0]-pos[1][0])) - np.arctan((pos[1][2]-pos[0][2])/(pos[1][0]-pos[0][0]))
                curvature = dalpha/ds
                self.rel_track_radius[tr].append([pos[0][0],curvature,1/curvature if np.abs(1/curvature) < 1e4 else 0])
                
            self.rel_track[tr]=np.array(rel_track[tr])
            self.rel_track_radius[tr]=np.array(rel_track_radius[tr])
    def plot2d(self, ax):
        if len(self.track) > 0:
            for i in self.conf.track_keys:
                tmp = self.track[i]['result']
                ax.plot(tmp[:,1],tmp[:,2],label=i)
            ax.invert_yaxis()
            #ax.set_aspect('equal')
    def rotate(tau1):
        '''２次元回転行列を返す。
        tau1: 回転角度 [rad]
        '''
        return np.array([[np.cos(tau1), -np.sin(tau1)], [np.sin(tau1),  np.cos(tau1)]])
