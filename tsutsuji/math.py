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

def interpolate_with_dist(track, element, cp_dist):
    def interpolate(data,ix,typ,cp_dist,base=0):
        return (data[:,typ][ix+1]-data[:,typ][ix])/(data[:,base][ix+1]-data[:,base][ix])*(cp_dist-data[:,base][ix])+data[:,typ][ix]
    min_ix = np.argmin(np.abs(track[:,0] - cp_dist))

    if min_ix > 0 and min_ix < len(track)-1:
        aroundzero = track[min_ix-1:min_ix+2]
        sign_dist = np.sign(aroundzero[:,0] - cp_dist)
        if sign_dist[0] != sign_dist[1]:
            result = interpolate(aroundzero,0,element,cp_dist)
        else:
            result = interpolate(aroundzero,1,element,cp_dist)
        #result = track[pos_ix][element]
    else:
        result = track[min_ix][element]
    return result

def calc_pl2xy(phi_deg, lambda_deg, phi0_deg, lambda0_deg):
    """ 緯度経度を平面直角座標に変換する
    - input:
        (phi_deg, lambda_deg): 変換したい緯度・経度[度]（分・秒でなく小数であることに注意）
        (phi0_deg, lambda0_deg): 平面直角座標系原点の緯度・経度[度]（分・秒でなく小数であることに注意）
    - output:
        x: 変換後の平面直角座標[m]
        y: 変換後の平面直角座標[m]
        
        原典
        https://qiita.com/sw1227/items/e7a590994ad7dcd0e8ab
    """
    # 緯度経度・平面直角座標系原点をラジアンに直す
    phi_rad = np.deg2rad(phi_deg)
    lambda_rad = np.deg2rad(lambda_deg)
    phi0_rad = np.deg2rad(phi0_deg)
    lambda0_rad = np.deg2rad(lambda0_deg)

    # 補助関数
    def A_array(n):
        A0 = 1 + (n**2)/4. + (n**4)/64.
        A1 = -     (3./2)*( n - (n**3)/8. - (n**5)/64. ) 
        A2 =     (15./16)*( n**2 - (n**4)/4. )
        A3 = -   (35./48)*( n**3 - (5./16)*(n**5) )
        A4 =   (315./512)*( n**4 )
        A5 = -(693./1280)*( n**5 )
        return np.array([A0, A1, A2, A3, A4, A5])

    def alpha_array(n):
        a0 = np.nan # dummy
        a1 = (1./2)*n - (2./3)*(n**2) + (5./16)*(n**3) + (41./180)*(n**4) - (127./288)*(n**5)
        a2 = (13./48)*(n**2) - (3./5)*(n**3) + (557./1440)*(n**4) + (281./630)*(n**5)
        a3 = (61./240)*(n**3) - (103./140)*(n**4) + (15061./26880)*(n**5)
        a4 = (49561./161280)*(n**4) - (179./168)*(n**5)
        a5 = (34729./80640)*(n**5)
        return np.array([a0, a1, a2, a3, a4, a5])

    # 定数 (a, F: 世界測地系-測地基準系1980（GRS80）楕円体)
    m0 = 0.9999 
    a = 6378137.
    F = 298.257222101

    # (1) n, A_i, alpha_iの計算
    n = 1. / (2*F - 1)
    A_array = A_array(n)
    alpha_array = alpha_array(n)

    # (2), S, Aの計算
    A_ = ( (m0*a)/(1.+n) )*A_array[0] # [m]
    S_ = ( (m0*a)/(1.+n) )*( A_array[0]*phi0_rad + np.dot(A_array[1:], np.sin(2*phi0_rad*np.arange(1,6))) ) # [m]

    # (3) lambda_c, lambda_sの計算
    lambda_c = np.cos(lambda_rad - lambda0_rad)
    lambda_s = np.sin(lambda_rad - lambda0_rad)

    # (4) t, t_の計算
    t = np.sinh( np.arctanh(np.sin(phi_rad)) - ((2*np.sqrt(n)) / (1+n))*np.arctanh(((2*np.sqrt(n)) / (1+n)) * np.sin(phi_rad)) )
    t_ = np.sqrt(1 + t*t)

    # (5) xi', eta'の計算
    xi2  = np.arctan(t / lambda_c) # [rad]
    eta2 = np.arctanh(lambda_s / t_)

    # (6) x, yの計算
    x = A_ * (xi2 + np.sum(np.multiply(alpha_array[1:],
                                       np.multiply(np.sin(2*xi2*np.arange(1,6)),
                                                   np.cosh(2*eta2*np.arange(1,6)))))) - S_ # [m]
    y = A_ * (eta2 + np.sum(np.multiply(alpha_array[1:],
                                        np.multiply(np.cos(2*xi2*np.arange(1,6)),
                                                    np.sinh(2*eta2*np.arange(1,6)))))) # [m]
    # return
    return x, y # [m]
