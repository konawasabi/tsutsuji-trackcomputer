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
        '''cfgファイルの読み込み
        '''
        self.conf = config.Config(path)
    def loadmap(self,to_load=None):
        '''mapファイルの読み込みと座標データ生成
        '''
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
    def relativepoint_single(self,to_calc,owntrack=None):
        '''owntrackを基準とした相対座標への変換
        Args:
             string
                 to_calc: 変換する軌道
             string
                 owntrack: 自軌道 (Option)
        Return:
             ndarray
                 [[owntrack基準の距離程, 変換後x座標成分(=0), 変換後y座標成分, 対応する軌道の距離程,絶対座標x成分,絶対座標y成分], ...]
        '''
        def interpolate(aroundzero,ix,typ):
            return (aroundzero[typ][ix+1]-aroundzero[typ][ix])/(aroundzero[0][ix+1]-aroundzero[0][ix])*(-aroundzero[0][ix])+aroundzero[typ][ix]
        owntrack = self.conf.owntrack if owntrack == None else owntrack
        tgt = self.track[to_calc]['result']
        src = self.track[owntrack]['result']
        len_tr = len(tgt)
        result = []
        # 自軌道に対する相対座標の算出
        for pos in src:
            tgt_xy = np.vstack((tgt[:,1],tgt[:,2]))
            tgt_xy_trans = np.dot(math.rotate(-pos[4]),(tgt_xy - np.vstack((pos[1],pos[2])) ) ) # 自軌道注目点を原点として座標変換
            min_ix = np.where(np.abs(tgt_xy_trans[0])==min(np.abs(tgt_xy_trans[0]))) # 変換後の座標でx'成分絶対値が最小となる点(=y'軸との交点)のインデックスを求める
            min_ix_val = min_ix[0][0]

            if min_ix_val > 0 and min_ix_val < len_tr-1: # y'軸との最近接点が軌道区間内にある場合
                aroundzero = np.vstack((tgt_xy_trans[0][min_ix_val-1:min_ix_val+2],\
                                        tgt_xy_trans[1][min_ix_val-1:min_ix_val+2]))
                aroundzero = np.vstack((aroundzero, tgt[:,0][min_ix_val-1:min_ix_val+2]))
                aroundzero = np.vstack((aroundzero, tgt[:,1][min_ix_val-1:min_ix_val+2]))
                aroundzero = np.vstack((aroundzero, tgt[:,2][min_ix_val-1:min_ix_val+2]))
                signx = np.sign(aroundzero[0])
                if signx[0] != signx[1]:
                    #y0 = (aroundzero[1][1]-aroundzero[1][0])/(aroundzero[0][1]-aroundzero[0][0])*(-aroundzero[0][0])+aroundzero[1][0]
                    #kp0 = (aroundzero[2][1]-aroundzero[2][0])/(aroundzero[0][1]-aroundzero[0][0])*(-aroundzero[0][0])+aroundzero[2][0]
                    result.append([pos[0],\
                                   0,\
                                   interpolate(aroundzero,0,1),\
                                   interpolate(aroundzero,0,2),\
                                   interpolate(aroundzero,0,3),\
                                   interpolate(aroundzero,0,4)])
                elif signx[1] != signx[2]:
                    #y0 = (aroundzero[1][2]-aroundzero[1][1])/(aroundzero[0][2]-aroundzero[0][1])*(-aroundzero[0][1])+aroundzero[1][1]
                    #kp0 = (aroundzero[2][2]-aroundzero[2][1])/(aroundzero[0][2]-aroundzero[0][1])*(-aroundzero[0][1])+aroundzero[2][1]
                    #result.append([pos[0], 0,y0,kp0])
                    result.append([pos[0],\
                                   0,\
                                   interpolate(aroundzero,1,1),\
                                   interpolate(aroundzero,1,2),\
                                   interpolate(aroundzero,1,3),\
                                   interpolate(aroundzero,1,4)])
            else:
                result.append([pos[0],\
                               tgt_xy_trans[0][min_ix][0],\
                               tgt_xy_trans[1][min_ix][0],\
                               tgt[:,0][min_ix][0],\
                               tgt[:,1][min_ix][0],\
                               tgt[:,2][min_ix][0]]) # y'軸との交点での自軌道距離程、x'成分(0になるべき)、y'成分(相対距離)を出力
        return(np.array(result))
    def relativepoint_all(self,owntrack=None):
        '''読み込んだ全ての軌道についてowntrackを基準とした相対座標への変換。
        '''
        owntrack = self.conf.owntrack if owntrack == None else owntrack
        calc_track = [i for i in self.conf.track_keys if i != owntrack]
        for tr in calc_track:
            self.rel_track[tr]=self.relativepoint_single(tr,owntrack)
    def relativeradius(self,to_calc=None,owntrack=None):
        owntrack = self.conf.owntrack if owntrack == None else owntrack
        calc_track = [i for i in self.conf.track_keys if i != owntrack] if to_calc == None else [to_calc]
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
    def relativeradius_cp(self,to_calc=None,owntrack=None,cp_dist=None):
        owntrack = self.conf.owntrack if owntrack == None else owntrack
        calc_track = [i for i in self.conf.track_keys if i != owntrack] if to_calc == None else [to_calc]
        if cp_dist == None:
            cp_dist = []
            for dat in self.track[owntrack]['data'].own_track.data:
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
    def plot_controlpoints(self,ax,owntrack = None):
        '''
        '''

        # 自軌道制御点の処理
        owntrack = self.conf.owntrack if owntrack == None else owntrack
        cp_ownt,pos_ownt  = self.takecp(owntrack) # 自軌道の制御点距離程を抽出
        rel_cp = None
        for tr in [i for i in self.conf.track_keys if i != owntrack]:
            cp_tr, pos_cp_tr = self.takecp(tr) # 注目している軌道の制御点座標データを抽出（注目軌道基準の座標）
            relativecp = self.convert_relativecp(tr,pos_cp_tr) # 自軌道基準の距離程に変換
            cp_tr_ownt = sorted(set(cp_ownt + cp_tr)) # 自軌道制御点との和をとる
            rel_cp_tmp = np.vstack((np.hstack((pos_ownt[:,1],relativecp[:,5])),np.hstack((pos_ownt[:,2],relativecp[:,6])))).T
            rel_cp = np.vstack((rel_cp,rel_cp_tmp)) if rel_cp != None else rel_cp_tmp
            for data in relativecp:
                ax.plot([data[1],data[5]],[data[2],data[6]],color='black')
        ax.scatter(rel_cp[:,0],rel_cp[:,1])
        print(owntrack)
        print('cp:',cp_tr_ownt)

        
        # 他軌道制御点の処理
        for key in [i for i in self.conf.track_keys if i != owntrack]:
            # 注目軌道の制御点を抽出
            cp_dist, pos_cp = self.takecp(key)
            ownt_relcp = self.relativepoint_single(key)
            
            print(key)
            print('cp:',cp_dist)
            ownt_relcp = np.hstack((ownt_relcp[np.isin(ownt_relcp[:,0],cp_ownt)],pos_ownt))
            ax.scatter(pos_cp[:,1],pos_cp[:,2])
            ax.scatter(ownt_relcp[:,4],ownt_relcp[:,5])
            for data in ownt_relcp:
                ax.plot([data[4],data[7]],[data[5],data[8]],color='red')
            
    def takecp(self,trackkey,owntrack = None):
        ''' 注目軌道の制御点を抽出
        Args:
                 trackkey (string): 
                 owntrack (string): 
        Returns:
                 list
                    cp_dist: 注目軌道の制御点距離程
                 list
                    pos_cp: 制御点における軌道座標データ
        '''
        owntrack = self.conf.owntrack if owntrack == None else owntrack
        cp_dist = []
        for dat in self.track[trackkey]['data'].own_track.data: # 軌道要素が存在する距離程を抽出
            cp_dist.append(dat['distance'])
        for dat in self.conf.track_data[trackkey]['supplemental_cp']: # supplemental_cpの追加
            cp_dist.append(dat)
        cp_dist = sorted(set(cp_dist))
        pos_cp = self.track[trackkey]['result'][np.isin(self.track[trackkey]['result'][:,0],cp_dist)]
        return cp_dist, pos_cp
    def convert_relativecp(self,trackkey,pos_cp,owntrack = None):
        ''' 抽出した制御点を自軌道座標に変換
        Return: 
                ndarray
                   resultcp: [注目軌道基準の距離程, 注目軌道基準のx, y座標, 自軌道基準制御点の距離程, 自軌道基準のx方向距離, 自軌道基準制御点のx, y座標] 
        '''
        owntrack = self.conf.owntrack if owntrack == None else owntrack
        target = self.track[owntrack]['result'][:,1:3]
        kp_cp = []
        rel_dist = []
        resultcp = []
        for data in pos_cp:
            inputpos = np.array([data[1],data[2]])
            result = math.minimumdist(target,inputpos)
            resultcp.append([data[0],inputpos[0],inputpos[1],math.cross_kilopost(self.track[owntrack]['result'],result),result[0],result[1][0],result[1][1]])
        return np.array(resultcp)
    def generate_mapdata(self):
        # import pdb
        self.relativepoint_all() # 全ての軌道データを自軌道基準の座標に変換
        self.relativeradius() # 全ての軌道データを自軌道基準の相対曲率半径を算出
        cp_ownt,_  = self.takecp(self.conf.owntrack) # 自軌道の制御点距離程を抽出
        for tr in [i for i in self.conf.track_keys if i != self.conf.owntrack]:
            _, pos_cp_tr = self.takecp(tr) # 注目している軌道の制御点座標データを抽出（注目軌道基準の座標）
            #pdb.set_trace()
            relativecp = self.convert_relativecp(tr,pos_cp_tr) # 自軌道基準の距離程に変換
            cp_tr_ownt = sorted(set(cp_ownt + list(relativecp[:,0]))) # 自軌道制御点との和をとる
            
            self.relativeradius_cp(to_calc=tr,cp_dist=cp_tr_ownt) # 制御点毎の相対半径を算出
            for data in self.rel_track_radius_cp[tr]:
                print('{:.2f};'.format(data[0]))
                print('Track[\''+tr+'\'].X.Interpolate({:.2f},{:.2f});'.format(data[3],data[2]))
