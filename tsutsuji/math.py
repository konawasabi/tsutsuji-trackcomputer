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

import numpy as np

def rotate(tau1):
    '''２次元回転行列を返す。

    tau1: 回転角度 [rad]
    '''
    return np.array([[np.cos(tau1), -np.sin(tau1)], [np.sin(tau1),  np.cos(tau1)]])

def minimumdist(track,p):
    '''二次元曲線trackについて、座標pから最も近い曲線上の点を求める。
    trackの点間は線形補間される。
    
    Args:
        track (ndarray):
            np.array([x0,y0],[x1,y1],...,[xn,yn])
        p (ndarray):
            np.array([xp,yp])

    Returns:
        float
            mindist: 曲線交点との距離
        ndarray
            crosspt: 曲線との交点座標
        int
            min_ix: track中で最もpに近い点のindex
        int
            second_min_ix: 最もpに近い点が含まれる区間の他端index。直交点が見つからない場合は-1。
    '''
    
    dist = (track - p)**2
    min_ix = np.argmin(np.sqrt(dist[:,0]+dist[:,1]))

    def distance(source, index):
        return np.sqrt(source[index][0]+source[index][1])

    if min_ix < len(dist)-1 and min_ix > 0:
        around_min = [distance(dist,min_ix-1),distance(dist,min_ix),distance(dist,min_ix+1)]

        second_min_ix = min_ix + 1

        lenAC = np.sqrt((track[second_min_ix][0] - track[min_ix][0])**2+(track[second_min_ix][1] - track[min_ix][1])**2)
        n = np.array([(track[second_min_ix][0] - track[min_ix][0])/lenAC,(track[second_min_ix][1] - track[min_ix][1])/lenAC])       
        a =np.array([track[min_ix][0],track[min_ix][1]])

        alpha = -np.dot(a-p,n)    
        mindist=(np.linalg.norm(a-p+alpha*n))
        crosspt=(a+alpha*n)

        # 求めたcrossptがtrack[min_ix] ~ track[second_min_ix]の間にない場合
        if crosspt[0]< track[min_ix][0] or crosspt[0]> track[second_min_ix][0]:
            second_min_ix = min_ix - 1

            lenAC = np.sqrt((track[min_ix][0] - track[second_min_ix][0])**2+(track[min_ix][1] - track[second_min_ix][1])**2)
            n = np.array([(track[min_ix][0] - track[second_min_ix][0])/lenAC,(track[min_ix][1] - track[second_min_ix][1])/lenAC])
            a = np.array([track[second_min_ix][0],track[second_min_ix][1]])

            alpha = -np.dot(a-p,n)    
            mindist = (np.linalg.norm(a-p+alpha*n))
            crosspt = (a+alpha*n)
    else:
        mindist=(distance(dist,min_ix))
        crosspt=(track[min_ix])
        second_min_ix = -1
        #print(p,mindist,crosspt,min_ix,second_min_ix)

    return mindist, crosspt, min_ix, second_min_ix

def cross_kilopost(track, result):
    '''minimumdistで求めたtrack上の最近傍点について、対応する距離程を求める。
    
    Args:
        track (ndarray):
            np.array([x0,y0],[x1,y1],...,[xn,yn])
        result (list):
            minimumdistの出力

    Return:
        float: 最近傍点の距離程。track端点が最近傍点の場合はNone
    '''
    if result[3]>0:
        subdist = np.sqrt((track[result[2]][1]-result[1][0])**2+(track[result[2]][2]-result[1][1])**2)
        if result[3] < result[2]:
            subdist *= -1
        kilopost = track[result[2]][0] + subdist
    else:
        kilopost = track[result[2]][0]
    return kilopost

def cross_normal(position, track):
    '''曲線trackの法線のうち、positionを通過するものを求める

    Args:
         ndarray
            position: np.array([x,y])
         ndarray
            track: np.array([[x0,y0],[x1,y1],...,[xn,yn]])

    Return:
    '''
    return None
def angle_twov(phiA, phiB):
    eA = np.array([np.cos(phiA),np.sin(phiA)])
    eB = np.array([np.cos(phiB),np.sin(phiB)])
    return np.arccos(np.dot(eA,eB))*np.sign(np.cross(eA,eB))
