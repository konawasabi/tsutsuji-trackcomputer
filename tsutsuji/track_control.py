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

import os
import pathlib
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate
import re

from kobushi import mapinterpreter
from kobushi import trackgenerator

from . import config
from . import math
from . import kml2track
from . import kp_offset

class TrackControl():
    def __init__(self):
        self.track = {}
        self.rel_track = {}
        self.rel_track_radius = {}
        self.rel_track_radius_cp = {}
        self.conf = None
        self.path = None
        self.generated_othertrack = None
        self.pointsequence_track = kml2track.Kml2track()
        self.exclude_tracks = []
    def loadcfg(self,path):
        '''cfgファイルの読み込み
        '''
        self.conf = config.Config(path)
        self.path = path
    def loadmap(self,to_load=None):
        '''mapファイルの読み込みと座標データ生成

        '''

        if False:
            import pdb
            pdb.set_trace()
        
        if self.conf != None:
            self.track = {}
            self.rel_track = {}
            self.rel_track_radius = {}
            self.rel_track_radius_cp = {}
            self.generated_othertrack = None
            self.pointsequence_track.initialize_variables()

            for i in self.conf.track_keys:
                self.track[i] = {}
                self.track[i]['interp'] = mapinterpreter.ParseMap(env=None,parser=None)
                self.track[i]['data'] = self.track[i]['interp'].load_files(self.conf.track_data[i]['file'])
                
                if self.conf.track_data[i]['endpoint'] > max(self.track[i]['data'].controlpoints.list_cp):
                    endkp = self.conf.track_data[i]['endpoint']
                else:
                    endkp = max(self.track[i]['data'].controlpoints.list_cp)
                    
                self.track[i]['data'].cp_arbdistribution = [min(self.track[i]['data'].controlpoints.list_cp),\
                                                            endkp + self.conf.general['unit_length'],\
                                                            self.conf.general['unit_length']]
                # endpoint + unit_lengthとすることで、endpointを確実に含ませる

                # 原点座標の処理
                if self.conf.track_data[i]['absolute_coordinate'] == True:
                    self.track[i]['tgen'] = trackgenerator.TrackGenerator(self.track[i]['data'],\
                                                                    x0 = self.conf.track_data[i]['z'],\
                                                                    y0 = self.conf.track_data[i]['x'],\
                                                                    z0 = self.conf.track_data[i]['y'],\
                                                                    theta0 = np.deg2rad(self.conf.track_data[i]['angle']))
                else:
                    if self.conf.track_data[i]['parent_track'] not in self.track.keys():
                        raise Exception('invalid trackkey: {:s}'.format(self.conf.track_data[i]['parent_track']))

                    pos_origin_abs = []
                    for j in range(0,5):
                        pos_origin_abs.append(math.interpolate_with_dist(self.track[self.conf.track_data[i]['parent_track']]['result'],\
                                                                         j,self.conf.track_data[i]['origin_kilopost']))

                    pos_origin_rot = np.dot(math.rotate(pos_origin_abs[4]),\
                                            np.array([self.conf.track_data[i]['z'],self.conf.track_data[i]['x']]))
                    self.track[i]['tgen'] = trackgenerator.TrackGenerator(self.track[i]['data'],\
                                                                    x0 = pos_origin_rot[0] + pos_origin_abs[1],\
                                                                    y0 = pos_origin_rot[1] + pos_origin_abs[2],\
                                                                    z0 = self.conf.track_data[i]['y'] + pos_origin_abs[3],\
                                                                    theta0 = np.deg2rad(self.conf.track_data[i]['angle']) + pos_origin_abs[4])
                self.track[i]['result'] = self.track[i]['tgen'].generate_owntrack()
                self.track[i]['cplist_symbol'] = self.take_cp_by_types(self.track[i]['data'].own_track.data)
                self.track[i]['toshow'] = True
                self.track[i]['output_mapfile'] = None

                # 従属する他軌道座標データを生成
                self.track[i]['data'].owntrack_pos = self.track[i]['result']
                self.track[i]['data'].owntrack_curve = self.track[i]['tgen'].generate_curveradius_dist()

                self.track[i]['othertrack'] = {}
                for otkey in self.track[i]['data'].othertrack.data.keys():
                    self.track[i]['othertrack'][otkey] = {}
                    otdata = self.track[i]['othertrack'][otkey]
                    otdata['tgen'] = trackgenerator.OtherTrackGenerator(self.track[i]['data'],otkey)
                    otdata['toshow'] = True
                    otdata['color'] = self.conf.track_data[i]['color']#.copy()

                    result_tmp = otdata['tgen'].generate()
                    result_theta = []
                    ix = 0
                    while ix<len(result_tmp)-1: # 生成した座標データに方位情報を追加する
                        data = result_tmp[ix]
                        result_theta.append([data[0],\
                                             data[1],\
                                             data[2],\
                                             data[3],\
                                             np.arctan((result_tmp[ix+1][2]-result_tmp[ix][2])/((result_tmp[ix+1][1]-result_tmp[ix][1]))),\
                                             0,\
                                             0,\
                                             data[4],\
                                             data[5],\
                                             data[6],\
                                             data[7]])
                        # [距離程, x, y, z, theta, radius(=0), gradient(=0), interpolate_func, cant, center, gauge]
                        ix +=1
                    data = result_tmp[ix]
                    result_theta.append([data[0],\
                                         data[1],\
                                         data[2],\
                                         data[3],\
                                         result_tmp[ix-1][4],\
                                         0,\
                                         0,\
                                         data[4],\
                                         data[5],\
                                         data[6],\
                                         data[7]])
                    otdata['result'] = np.array(result_theta)

        self.pointsequence_track.load_files(self.conf)
            
            
    def relativepoint_single(self,to_calc,owntrack=None,parent_track=None):
        '''owntrackを基準とした相対座標への変換

        Args:
             string
                 to_calc: 変換する軌道
             string
                 owntrack: 自軌道 (Option)
        Return:
             ndarray
                 [[owntrack基準の距離程, 変換後x座標成分(=0), 変換後y座標成分, 変換後z座標成分, 対応する軌道の距離程,絶対座標x成分,絶対座標y成分,絶対座標z成分,カント], ...]
        '''
        def interpolate(aroundzero,ix,typ,base='x_tr'):
            return (aroundzero[typ][ix+1]-aroundzero[typ][ix])/(aroundzero[base][ix+1]-aroundzero[base][ix])*(-aroundzero[base][ix])+aroundzero[typ][ix]
        def take_relpos_std(src,tgt):
            len_tr = len(tgt)
            result = []
            # 自軌道に対する相対座標の算出
            for pos in src:
                tgt_xy = np.vstack((tgt[:,1],tgt[:,2]))
                tgt_xy_trans = np.dot(math.rotate(-pos[4]),(tgt_xy - np.vstack((pos[1],pos[2])) ) ) # 自軌道注目点を原点として座標変換
                min_ix = np.where(np.abs(tgt_xy_trans[0])==min(np.abs(tgt_xy_trans[0]))) # 変換後の座標でx'成分絶対値が最小となる点(=y'軸との交点)のインデックスを求める
                min_ix_val = min_ix[0][0]

                if min_ix_val > 0 and min_ix_val < len_tr-1: # y'軸との最近接点が軌道区間内にある場合
                    aroundzero = {'x_tr':tgt_xy_trans[0][min_ix_val-1:min_ix_val+2],\
                                  'y_tr':tgt_xy_trans[1][min_ix_val-1:min_ix_val+2],\
                                  'kp':  tgt[:,0][min_ix_val-1:min_ix_val+2],\
                                  'x_ab':tgt[:,1][min_ix_val-1:min_ix_val+2],\
                                  'y_ab':tgt[:,2][min_ix_val-1:min_ix_val+2],\
                                  'z_ab':tgt[:,3][min_ix_val-1:min_ix_val+2],\
                                  'cant':tgt[:,8][min_ix_val-1:min_ix_val+2]}
                    # aroundzero : [変換後x座標成分, 変換後y座標成分, 対応する軌道の距離程, 絶対座標x成分, 絶対座標y成分]
                    signx = np.sign(aroundzero['x_tr'])
                    if signx[0] != signx[1]:
                        result.append([pos[0],\
                                       0,\
                                       interpolate(aroundzero,0,'y_tr'),\
                                       interpolate(aroundzero,0,'z_ab') - pos[3],\
                                       interpolate(aroundzero,0,'kp'),\
                                       interpolate(aroundzero,0,'x_ab'),\
                                       interpolate(aroundzero,0,'y_ab'),\
                                       interpolate(aroundzero,0,'z_ab'),\
                                       interpolate(aroundzero,0,'cant')])
                    elif signx[1] != signx[2]:
                        result.append([pos[0],\
                                       0,\
                                       interpolate(aroundzero,1,'y_tr'),\
                                       interpolate(aroundzero,1,'z_ab') - pos[3],\
                                       interpolate(aroundzero,1,'kp'),\
                                       interpolate(aroundzero,1,'x_ab'),\
                                       interpolate(aroundzero,1,'y_ab'),\
                                       interpolate(aroundzero,1,'z_ab'),\
                                       interpolate(aroundzero,1,'cant')])
                else:
                    result.append([pos[0],\
                                   tgt_xy_trans[0][min_ix][0],\
                                   tgt_xy_trans[1][min_ix][0],\
                                   tgt[:,3][min_ix][0] - pos[3],\
                                   tgt[:,0][min_ix][0],\
                                   tgt[:,1][min_ix][0],\
                                   tgt[:,2][min_ix][0],\
                                   tgt[:,3][min_ix][0],\
                                   tgt[:,8][min_ix][0]]) # y'軸との交点での自軌道距離程、x'成分(0になるべき)、y'成分(相対距離)を出力
            return result
        def take_relpos_owot(src,tgt):
            len_tr = len(tgt)
            result = []
            # 自軌道に対する相対座標の算出
            for pos in src:
                tgt_xy = np.vstack((tgt[:,1],tgt[:,2]))
                tgt_xy_trans = np.dot(math.rotate(-pos[4]),(tgt_xy - np.vstack((pos[1],pos[2])) ) ) # 自軌道注目点を原点として座標変換
                min_ix = np.where(np.abs(tgt_xy_trans[0])==min(np.abs(tgt_xy_trans[0]))) # 変換後の座標でx'成分絶対値が最小となる点(=y'軸との交点)のインデックスを求める
                min_ix_val = min_ix[0][0]

                if min_ix_val > 0 and min_ix_val < len_tr-1: # y'軸との最近接点が軌道区間内にある場合
                    aroundzero = {'x_tr':tgt_xy_trans[0][min_ix_val-1:min_ix_val+2],\
                                  'y_tr':tgt_xy_trans[1][min_ix_val-1:min_ix_val+2],\
                                  'kp':  tgt[:,0][min_ix_val-1:min_ix_val+2],\
                                  'x_ab':tgt[:,1][min_ix_val-1:min_ix_val+2],\
                                  'y_ab':tgt[:,2][min_ix_val-1:min_ix_val+2],\
                                  'z_ab':tgt[:,3][min_ix_val-1:min_ix_val+2],\
                                  'cant':tgt[:,8][min_ix_val-1:min_ix_val+2]}
                    # aroundzero : [変換後x座標成分, 変換後y座標成分, 対応する軌道の距離程, 絶対座標x成分, 絶対座標y成分]
                    signx = np.sign(aroundzero['x_tr'])
                    if signx[0] != signx[1]:
                        result.append([pos[0],\
                                       0,\
                                       interpolate(aroundzero,0,'y_tr'),\
                                       interpolate(aroundzero,0,'z_ab') - pos[3],\
                                       interpolate(aroundzero,0,'kp'),\
                                       interpolate(aroundzero,0,'x_ab'),\
                                       interpolate(aroundzero,0,'y_ab'),\
                                       interpolate(aroundzero,0,'z_ab'),\
                                       interpolate(aroundzero,0,'cant')])
                    elif signx[1] != signx[2]:
                        result.append([pos[0],\
                                       0,\
                                       interpolate(aroundzero,1,'y_tr'),\
                                       interpolate(aroundzero,1,'z_ab') - pos[3],\
                                       interpolate(aroundzero,1,'kp'),\
                                       interpolate(aroundzero,1,'x_ab'),\
                                       interpolate(aroundzero,1,'y_ab'),\
                                       interpolate(aroundzero,1,'z_ab'),\
                                       interpolate(aroundzero,1,'cant')])
                else:
                    result.append([pos[0],\
                                   tgt_xy_trans[0][min_ix][0],\
                                   tgt_xy_trans[1][min_ix][0],\
                                   tgt[:,3][min_ix][0] - pos[3],\
                                   tgt[:,0][min_ix][0],\
                                   tgt[:,1][min_ix][0],\
                                   tgt[:,2][min_ix][0],\
                                   tgt[:,3][min_ix][0],\
                                   tgt[:,8][min_ix][0]]) # y'軸との交点での自軌道距離程、x'成分(0になるべき)、y'成分(相対距離)を出力
            return result
        
        owntrack = self.conf.owntrack if owntrack == None else owntrack
        src = self.track[owntrack]['result']
        if parent_track is not None:
            tgt = self.track[parent_track]['othertrack'][to_calc]['result']
            result = take_relpos_owot(src,tgt)
        elif '@' not in to_calc:
            tgt = self.track[to_calc]['result']
            result = take_relpos_std(src,tgt)
        else:
            tgt = self.pointsequence_track.track[to_calc]['result']
            result = take_relpos_std(src,tgt)
        return(np.array(result))
    def relativepoint_all(self,owntrack=None):
        '''読み込んだ全ての軌道についてowntrackを基準とした相対座標への変換。

        '''
        owntrack = self.conf.owntrack if owntrack == None else owntrack
        calc_track = [i for i in self.conf.track_keys + self.conf.kml_keys + self.conf.csv_keys if i != owntrack]
        for tr in calc_track:
            self.rel_track[tr]=self.relativepoint_single(tr,owntrack)

        calc_track = [i for i in self.conf.track_keys if i != owntrack]
        for tr in calc_track:
            for ottr in self.track[tr]['othertrack'].keys():
                self.rel_track['@OT_{:s}@_{:s}'.format(tr,ottr)] = self.relativepoint_single(ottr,owntrack,parent_track=tr)
    def relativeradius(self,to_calc=None,owntrack=None):
        owntrack = self.conf.owntrack if owntrack == None else owntrack
        if to_calc is None:
            calc_track = self.get_trackkeys(owntrack)
        else:
            calc_track = to_calc
        for tr in calc_track:
            self.rel_track_radius[tr] = []

            # 注目軌道相対座標を線形補間する
            x_interp = np.linspace(min(self.rel_track[tr][:,0]),max(self.rel_track[tr][:,0]),int((max(self.rel_track[tr][:,0])-min(self.rel_track[tr][:,0]))/1.0)+1)
            f_xy = interpolate.interp1d(self.rel_track[tr][:,0],self.rel_track[tr][:,2])
            f_z  = interpolate.interp1d(self.rel_track[tr][:,0],self.rel_track[tr][:,3])
            input_np = np.vstack((np.vstack((x_interp,f_xy(x_interp))),f_z(x_interp))).T
            
            # 相対曲率半径の算出
            for ix in range(0,len(input_np)-2):
                pos = []
                pos.append(input_np[ix])
                pos.append(input_np[ix+1])
                pos.append(input_np[ix+2])

                # 幾何学的に曲率を求める(xy平面)
                ds = np.sqrt((pos[1][0]-pos[0][0])**2 + (pos[1][1]-pos[0][1])**2)
                dalpha = np.arctan((pos[2][1]-pos[1][1])/(pos[2][0]-pos[1][0])) \
                    - np.arctan((pos[1][1]-pos[0][1])/(pos[1][0]-pos[0][0]))
                curvature = dalpha/ds

                # 幾何学的に曲率を求める(z面)
                ds_z = np.sqrt((pos[1][0]-pos[0][0])**2 + (pos[1][2]-pos[0][2])**2)
                dalpha_z = np.arctan((pos[2][2]-pos[1][2])/(pos[2][0]-pos[1][0])) \
                    - np.arctan((pos[1][2]-pos[0][2])/(pos[1][0]-pos[0][0]))
                curvature_z = dalpha_z/ds_z
                
                self.rel_track_radius[tr].append([pos[0][0],\
                                                  curvature,\
                                                  1/curvature if np.abs(1/curvature) < 1e4 else 0,\
                                                  curvature_z,\
                                                  1/curvature_z if np.abs(1/curvature_z) < 1e4 else 0])
                
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

                if len(pos_cp) == 0:
                    ix+=1
                    continue

                len_section         = cp_dist[ix+1] - cp_dist[ix]
                curvature_section   = np.sum(pos_cp[:,1])/len_section
                curvature_section_z = np.sum(pos_cp[:,3])/len_section
                #yval = self.interpolate_with_dist(2,tr,cp_dist[ix])
                yval = math.interpolate_with_dist(self.rel_track[tr],2,cp_dist[ix])
                #zval = self.interpolate_with_dist(3,tr,cp_dist[ix])
                zval = math.interpolate_with_dist(self.rel_track[tr],3,cp_dist[ix])
                self.rel_track_radius_cp[tr].append([cp_dist[ix],\
                                                     curvature_section,\
                                                     1/curvature_section if np.abs(1/curvature_section) < 1e4 else 0,\
                                                     yval,\
                                                     curvature_section_z,\
                                                     1/curvature_section_z if np.abs(1/curvature_section_z) < 1e4 else 0,\
                                                     zval])
                ix+=1

            # 最終制御点の出力
            #yval = self.interpolate_with_dist(2,tr,cp_dist[ix])
            yval = math.interpolate_with_dist(self.rel_track[tr],2,cp_dist[ix])
            #zval = self.interpolate_with_dist(3,tr,cp_dist[ix])
            zval = math.interpolate_with_dist(self.rel_track[tr],3,cp_dist[ix])
            curvature_section   = np.inf
            curvature_section_z = np.inf
            self.rel_track_radius_cp[tr].append([cp_dist[ix],\
                                     curvature_section,\
                                     1/curvature_section if np.abs(1/curvature_section) < 1e4 else 0,\
                                     yval,\
                                     curvature_section_z,\
                                     1/curvature_section_z if np.abs(1/curvature_section_z) < 1e4 else 0,\
                                     zval])
            self.rel_track_radius_cp[tr] = np.array(self.rel_track_radius_cp[tr])
    def plot2d(self, ax):
        if len(self.track) > 0:
            for i in self.conf.track_keys:
                if self.track[i]['toshow']:
                    tmp = self.track[i]['result']
                    ax.plot(tmp[:,1],tmp[:,2],label=i,color=self.conf.track_data[i]['color'])
                if len(self.track[i]['othertrack'])>0:
                    for otkey in self.track[i]['othertrack'].keys():
                        if self.track[i]['othertrack'][otkey]['toshow']:
                            tmp = self.track[i]['othertrack'][otkey]['result']
                            ax.plot(tmp[:,1],tmp[:,2],\
                                    label='{:s}_{:s}'.format(i,otkey),\
                                    color=self.track[i]['othertrack'][otkey]['color'],\
                                    lw=1)
            #ax.invert_yaxis()
            #ax.set_aspect('equal')
            self.pointsequence_track.plot2d(ax)
        if self.generated_othertrack is not None:
            for otrack in self.generated_othertrack.keys():
                if self.generated_othertrack[otrack]['toshow']:
                    tmp = self.generated_othertrack[otrack]['data']
                    tmp = tmp[tmp[:,0]<=self.generated_othertrack[otrack]['distrange']['max']]
                    ax.plot(tmp[:,1],tmp[:,2],color=self.generated_othertrack[otrack]['color'])
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
            extent = self.pointsequence_track.drawarea(extent)
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
            rel_cp = np.vstack((rel_cp,rel_cp_tmp)) if rel_cp is not None else rel_cp_tmp
            for data in relativecp:
                ax.plot([data[1],data[5]],[data[2],data[6]],color='black')
        ax.scatter(rel_cp[:,0],rel_cp[:,1],color=self.conf.track_data[owntrack]['color'])
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
            ax.scatter(pos_cp[:,1],pos_cp[:,2],color=self.conf.track_data[key]['color'])
            ax.scatter(ownt_relcp[:,5],ownt_relcp[:,6],color=self.conf.track_data[key]['color'],marker='x')
            for data in ownt_relcp:
                ax.plot([data[5],data[10]],[data[6],data[11]],color='red',alpha=0.25)
            
    def takecp(self,trackkey,owntrack = None, elem=None, supplemental=True):
        ''' 注目軌道の制御点を抽出

        Args:
                 trackkey (string): 
                 owntrack (string):
                 elem     (string): elemで指定した要素のみ抽出する
        Returns:
                 list
                    cp_dist: 注目軌道の制御点距離程
                 list
                    pos_cp: 制御点における軌道座標データ
        '''
        owntrack = self.conf.owntrack if owntrack == None else owntrack
        cp_dist = []

        if '@' not in trackkey:
            for dat in self.track[trackkey]['data'].own_track.data: # 軌道要素が存在する距離程を抽出
                if elem == None or dat['key'] == elem:
                    cp_dist.append(dat['distance'])
            cp_dist.append(self.conf.track_data[trackkey]['endpoint'])
            cp_dist.append(0)
            if supplemental:
                for dat in self.conf.track_data[trackkey]['supplemental_cp']: # supplemental_cpの追加
                    cp_dist.append(dat)
            cp_dist = sorted(set(cp_dist))
            pos_cp = self.track[trackkey]['result'][np.isin(self.track[trackkey]['result'][:,0],cp_dist)]
        elif '@OT' in trackkey:
            parent_key = re.search('(?<=@OT_).+(?=@)',trackkey).group(0)#trackkey.split('@')[1].split('OT_')[1]
            child_key = trackkey.split('@_')[-1]
            for dat in self.track[parent_key]['othertrack'][child_key]['tgen'].data:
                if elem == None or dat['key'] == elem:
                    cp_dist.append(dat['distance'])
            cp_dist.append(0)

            if supplemental:
                parent_cp_dist,_ = self.takecp(parent_key) # 親軌道の制御点を求める
                cp_dist = sorted(set(cp_dist + parent_cp_dist)) # 注目する軌道と親軌道の制御点の和集合を求める
            else:
                cp_dist = sorted(set(cp_dist))

            pos_cp = self.track[parent_key]['othertrack'][child_key]['result'][np.isin(self.track[parent_key]['othertrack'][child_key]['result'][:,0],cp_dist)]
        else:
            for dat in self.pointsequence_track.track[trackkey]['result']:
                cp_dist.append(dat[0])
            cp_dist.append(0)
            cp_dist = sorted(set(cp_dist))
            pos_cp = self.pointsequence_track.track[trackkey]['result'][np.isin(self.pointsequence_track.track[trackkey]['result'][:,0],cp_dist)]
        
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
            if result[3] == -1 and result[2]>0:
                continue
            resultcp.append([data[0],\
                             inputpos[0],\
                             inputpos[1],\
                             math.cross_kilopost(self.track[owntrack]['result'],result),\
                             result[0],\
                             result[1][0],\
                             result[1][1]])
        return np.array(resultcp)
    def generate_mapdata(self):
        ''' self.conf.owntrackを基準とした他軌道構文データを生成, 出力する
        '''
        self.exclude_tracks = []
        if False:
            import pdb
            pdb.set_trace()

        self.relativepoint_all() # 全ての軌道データを自軌道基準の座標に変換
        self.relativeradius() # 全ての軌道データについて自軌道基準の相対曲率半径を算出
        cp_ownt,_  = self.takecp(self.conf.owntrack) # 自軌道の制御点距離程を抽出

        # owntrack以外の各軌道について処理する
        for tr in self.get_trackkeys(self.conf.owntrack):
            try:
                _, pos_cp_tr = self.takecp(tr) # 注目している軌道の制御点座標データを抽出（注目軌道基準の座標）
                relativecp = self.convert_relativecp(tr,pos_cp_tr) # 自軌道基準の距離程に変換
                cp_tr_ownt = sorted(set([i for i in cp_ownt if i<=max(relativecp[:,3]) and i>min(relativecp[:,3])] + list(relativecp[:,3]))) # 自軌道制御点のうち注目軌道が含まれる点と、自軌道基準に変換した注目軌道距離程の和をとる
            #cp_tr_ownt = sorted(list(relativecp[:,3])) # 
            
                self.relativeradius_cp(to_calc=tr,cp_dist=cp_tr_ownt) # 制御点毎の相対半径を算出
            except IndexError:
                # too many indices for array: array is 1-dimensional, but 2 were indexed に対する処理
                # = 自軌道基準の座標系で表せない軌道
                print('{:s}: IndexError. Generate has been ignored.'.format(tr))
                self.exclude_tracks.append(tr)
    

        # 他軌道構文生成
        for tr in [i for i in self.get_trackkeys(self.conf.owntrack) if i not in self.exclude_tracks]:
            output_map = {'x':'', 'y':'', 'cant':'', 'center':'', 'interpolate_func':'', 'gauge':''}
            if self.conf.general['offset_variable'] is not None:
                kp_val = '$'+self.conf.general['offset_variable']+' + '
            else:
                kp_val = ''

            for data in self.rel_track_radius_cp[tr]:
                if '@' not in tr or '@OT' in tr or (('@KML' in tr or '@CSV' in tr) and self.pointsequence_track.track[tr]['conf']['calc_relrad']):
                    output_map['x'] += '{:s}{:.2f};\n'.format(kp_val,data[0])
                    output_map['x'] += 'Track[\'{:s}\'].X.Interpolate({:.2f},{:.2f});\n'.format(tr,data[3],data[2])
                    output_map['y'] += '{:s}{:.2f};\n'.format(kp_val,data[0])
                    output_map['y'] += 'Track[\'{:s}\'].Y.Interpolate({:.2f},{:.2f});\n'.format(tr,data[6],data[5])
                else:
                    output_map['x'] += '{:s}{:.2f};\n'.format(kp_val,data[0])
                    output_map['x'] += 'Track[\'{:s}\'].X.Interpolate({:.2f},{:.2f});\n'.format(tr,data[3],0)
                    output_map['y'] += '{:s}{:.2f};\n'.format(kp_val,data[0])
                    output_map['y'] += 'Track[\'{:s}\'].Y.Interpolate({:.2f},{:.2f});\n'.format(tr,data[6],0)

            cp_dist = {}
            pos_cp = {}
            relativecp = {}
            for key in ['cant','interpolate_func','center','gauge']:
                cp_dist[key], pos_cp[key] = self.takecp(tr,elem=key,supplemental=False)
                relativecp[key] =  self.convert_relativecp(tr,pos_cp[key])

            if len(relativecp['cant'])>0:
                '''
                for data in self.rel_track[tr][np.isin(self.rel_track[tr][:,0],relativecp['cant'][:,0])]:
                    output_map['cant'] += '{:s}{:.2f};\n'.format(kp_val,data[0])
                    output_map['cant'] += 'Track[\'{:s}\'].Cant.Interpolate({:.3f});\n'.format(tr,data[8])
                '''
                for data in self.convert_cant_with_relativecp(tr,relativecp['cant'][:,3]):
                    output_map['cant'] += '{:s}{:.2f};\n'.format(kp_val,data[0])
                    output_map['cant'] += 'Track[\'{:s}\'].Cant.Interpolate({:.3f});\n'.format(tr,data[1])

            
            key = 'interpolate_func'
            if len(relativecp[key])>0:
                for index in range(len(relativecp[key])):
                    output_map[key] += '{:s}{:.2f};\n'.format(kp_val,relativecp[key][index][3])
                    output_map[key] += 'Track[\'{:s}\'].Cant.SetFunction({:d});\n'.format(tr,int(pos_cp[key][index][7]))
            
            key = 'center'
            if len(relativecp[key])>0:
                for index in range(len(relativecp[key])):
                    output_map[key] += '{:s}{:.2f};\n'.format(kp_val,relativecp[key][index][3])
                    output_map[key] += 'Track[\'{:s}\'].Cant.SetCenter({:.3f});\n'.format(tr,pos_cp[key][index][9])

            key = 'gauge'
            if len(relativecp[key])>0:
                for index in range(len(relativecp[key])):
                    output_map[key] += '{:s}{:.2f};\n'.format(kp_val,relativecp[key][index][3])
                    output_map[key] += 'Track[\'{:s}\'].Cant.SetGauge({:.3f});\n'.format(tr,pos_cp[key][index][10])

            output_file = ''
            output_file += 'BveTs Map 2.02:utf-8\n\n'
            # 他軌道構文印字
            if kp_val != '':
                output_file += '# offset\n'
                output_file += '${:s} = {:f};\n'.format(self.conf.general['offset_variable'],self.conf.general['origin_distance'])+'\n'
            output_file += '# Track[\'{:s}\'].X\n'.format(tr)
            output_file += output_map['x']+'\n'
            output_file += '# Track[\'{:s}\'].Y\n'.format(tr)
            output_file += output_map['y']+'\n'
            output_file += '# Track[\'{:s}\'].Cant.Interpolate\n'.format(tr)
            output_file += output_map['cant']+'\n'
            output_file += '# Track[\'{:s}\'].Cant.SetFunction\n'.format(tr)
            output_file += output_map['interpolate_func']+'\n'
            output_file += '# Track[\'{:s}\'].Cant.SetCenter\n'.format(tr)
            output_file += output_map['center']+'\n'
            output_file += '# Track[\'{:s}\'].Cant.SetGauge\n'.format(tr)
            output_file += output_map['gauge']+'\n'

            if '@' not in tr:
                self.track[tr]['output_mapfile'] = output_file
            elif '@OT' in tr:
                parent_key = re.search('(?<=@OT_).+(?=@)',tr).group(0)
                child_key = tr.split('@_')[-1]
                self.track[parent_key]['othertrack'][child_key]['output_mapfile'] = output_file
            else:
                self.pointsequence_track.track[tr]['conf']['output_mapfile'] = output_file
            
            #print(output_file)
            os.makedirs(self.conf.general['output_path'], exist_ok=True)
            f = open(self.conf.general['output_path'].joinpath(pathlib.Path('{:s}_converted.txt'.format(tr))),'w')
            f.write(output_file)
            f.close()
            print(self.conf.general['output_path'].joinpath(pathlib.Path('{:s}_converted.txt'.format(tr))))

        # 自軌道データの距離程をoffsetして出力
        owntrack_kpoffs = []
        owntrack_input, owntrack_root = kp_offset.procpath(self.conf.track_data[self.conf.owntrack]['file'])
        kp_offset.readfile(owntrack_input,\
                           '$'+self.conf.general['offset_variable'],\
                           self.conf.general['origin_distance'],\
                           owntrack_kpoffs,\
                           owntrack_root)
        kp_offset.writefile(owntrack_kpoffs,\
                            self.conf.general['output_path'].joinpath('owntrack'))
    def convert_cant_with_relativecp(self, tr, cp_dist):
        ''' trで指定した軌道について、対応する距離程でのカントを求める 
        '''
        result = []
        for cp in cp_dist:
            #result.append([cp, self.interpolate_with_dist(8,tr,cp)])
            result.append([cp, math.interpolate_with_dist(self.rel_track[tr],8,cp)])
        
        return result
    def take_cp_by_types(self, source, types=None):
        '''軌道要素が存在する距離程を要素毎にリスト化する
        '''
        cplist = {}
        for typ in ['radius', 'gradient', 'interpolate_func', 'cant', 'center', 'gauge']:
            cplist[typ] = []
        for data in source:
            if data['key'] in ['radius', 'gradient', 'interpolate_func', 'cant', 'center', 'gauge']:
                cplist[data['key']].append(data['distance'])
        return cplist
    def plot_symbols(self, ax, symboltype, size=20):
        ''' 制御点座標をプロットする
        '''
        symbol_plot = {'radius':'o', 'gradient':'^', 'supplemental_cp':'x', 'track':'+'}
        if len(self.track.keys()) > 0:
            for tr_l in self.conf.track_keys:
                if self.track[tr_l]['toshow'] and symboltype != 'track':
                    if symboltype == 'supplemental_cp':
                        pos = self.track[tr_l]['result'][np.isin(self.track[tr_l]['result'][:,0],self.conf.track_data[tr_l]['supplemental_cp'])]
                    else:
                        pos = self.track[tr_l]['result'][np.isin(self.track[tr_l]['result'][:,0],self.track[tr_l]['cplist_symbol'][symboltype])]
                    ax.scatter(pos[:,1],pos[:,2],color=self.conf.track_data[tr_l]['color'],marker=symbol_plot[symboltype],alpha=0.75,s=size)
                elif symboltype == 'track':
                    for tr_ot in self.track[tr_l]['othertrack'].keys():
                        trackdata = self.track[tr_l]['othertrack'][tr_ot]
                        if trackdata['toshow']:
                            cp_dist = []
                            for cp in trackdata['tgen'].data:
                                cp_dist.append(cp['distance'])
                            pos = trackdata['result'][np.isin(trackdata['result'][:,0],cp_dist)]
                            ax.scatter(pos[:,1],pos[:,2],color=trackdata['color'],marker=symbol_plot[symboltype],alpha=0.75,s=size)
                            
                        
                    
    def generate_otdata(self):
        ''' generate結果から他軌道座標データを生成する
        '''
        
        if False:
            import pdb
            pdb.set_trace()

        # generate結果をincludeする擬似マップファイルを生成
        output_file = ''

        # 自軌道ファイルをinclude
        path = self.conf.general['output_path'].joinpath(pathlib.Path('owntrack')).joinpath(self.conf.track_data[self.conf.general['owntrack']]['file'].name)
        #output_file += 'include \'{:s}\';\n'.format(str(path))
        output_file += self.read_owntrackmap(path)

        # 他軌道ファイルをinclude
        otlist = self.get_trackkeys(self.conf.general['owntrack'])
        for tr_l in [i for i in otlist if (i not in self.exclude_tracks)]:
            path = self.conf.general['output_path'].joinpath(pathlib.Path('{:s}_converted.txt'.format(tr_l)))
            output_file += 'include \'{:s}\';\n'.format(str(path))

        otmap_path = self.conf.general['output_path'].joinpath(pathlib.Path('tmpmap.txt'))

        # kobushi-trackviewerのマップパーサーへoutput_fileを渡す
        ot_interp = mapinterpreter.ParseMap(env=None,parser=None)
        self.ot_map_source = ot_interp.load_files(None,\
                                                  datastring = output_file,\
                                                  virtualroot = pathlib.Path(self.conf.general['output_path']),\
                                                  virtualfilename = otmap_path)

        # 座標生成する距離程範囲を設定
        if self.conf.track_data[self.conf.general['owntrack']]['endpoint'] > max(self.track[self.conf.general['owntrack']]['data'].controlpoints.list_cp):
            endkp = self.conf.track_data[self.conf.general['owntrack']]['endpoint']
        else:
            endkp = max(self.track[self.conf.general['owntrack']]['data'].controlpoints.list_cp)
        self.ot_map_source.cp_arbdistribution = [min(self.track[self.conf.general['owntrack']]['data'].controlpoints.list_cp)+self.conf.general['origin_distance'],\
                                            endkp + self.conf.general['unit_length'],\
                                            self.conf.general['unit_length']]

        # kobushi-trackviewerの軌道ジェネレータで自軌道座標を生成
        self.ot_data_ownt = trackgenerator.TrackGenerator(self.ot_map_source,\
                                                     x0 = self.conf.track_data[self.conf.general['owntrack']]['z'],\
                                                     y0 = self.conf.track_data[self.conf.general['owntrack']]['x'],\
                                                     z0 = self.conf.track_data[self.conf.general['owntrack']]['y'],\
                                                     theta0 = np.deg2rad(self.conf.track_data[self.conf.general['owntrack']]['angle']))
        self.ot_map_source.owntrack_pos = self.ot_data_ownt.generate_owntrack()

        # 他軌道座標、プロット制御パラメータを生成
        self.generated_othertrack = {}
        for key in self.ot_map_source.othertrack.data.keys():
            generator = trackgenerator.OtherTrackGenerator(self.ot_map_source,key)
            self.generated_othertrack[key]={'data':generator.generate(),\
                                            'toshow':True,\
                                            'color':'#000000',\
                                            #'controlpoints':[i['distance'] for i in self.ot_map_source.othertrack.data[key]],\
                                            'distrange':generator.distrange}
    def get_trackkeys(self,owntrack):
        calc_track = [i for i in self.conf.track_keys if i!=owntrack]
        calc_track += self.conf.kml_keys
        calc_track += self.conf.csv_keys

        
        for tr in [i for i in self.conf.track_keys if i != owntrack]:
            for ottr in self.track[tr]['othertrack'].keys():
                calc_track.append('@OT_{:s}@_{:s}'.format(tr,ottr))
        return calc_track
    def read_owntrackmap(self,filepath,rootpath = None):
        mapdata = ''
        input_path     = pathlib.Path(filepath)
        #input_parent   = input_path.parent
        #input_filename = input_path.name
        if rootpath is None:
            path = input_path
        else:
            path = pathlib.Path(rootpath).joinpath(input_path.name)
        with open(path, mode='r') as fp:
            mapdata = fp.read()
        mapdata = re.sub('BveTs Map 2.02.*?\n', '', mapdata)

        str_pointer = 0
        result = ''
        while(True):
            m = re.search('include(\s)*\'.*\'(\s)*;',mapdata)
            if m is None:
                result += mapdata
                break
            else:
                result += mapdata[:(m.span())[0]]
                arg_include = re.search('(?<=include\s\').*?(?=\';)',m.group(0))
                filepath = pathlib.Path(arg_include.group(0))
                result += self.read_owntrackmap(filepath, rootpath=input_path.parent)
                mapdata = mapdata[m.span()[1]:]
        
        return result
        
