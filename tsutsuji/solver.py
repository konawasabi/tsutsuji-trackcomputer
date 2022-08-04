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
from kobushi import trackcoordinate as tc
from . import math
from . import curvetrackplot

class solver():
    def __init__(self):
        self.ci = tc.curve_intermediate()
        self.cgen = tc.curve()
    def temporal_trackparam(self,Rtmp,lenTC1,lenTC2,A,B,phiA,phiB,tranfunc):
        delta_phi = math.angle_twov(phiA,phiB) #曲線前後での方位変化
            
        if(lenTC1>0):
            tc1_tmp = self.ci.transition_curve(lenTC1,\
                                          0,\
                                          Rtmp,\
                                          phiA,\
                                          tranfunc,\
                                          lenTC1) # 入口側の緩和曲線
        else:
            tc1_tmp=(np.array([0,0]),0,0)

        if(lenTC2>0):
            tc2_tmp = self.ci.transition_curve(lenTC2,\
                                          Rtmp,\
                                          0,\
                                          0,\
                                          tranfunc,\
                                          lenTC2) # 出口側の緩和曲線
        else:
            tc2_tmp=(np.array([0,0]),0,0)

        phi_circular = delta_phi - tc1_tmp[1]-tc2_tmp[1] # 円軌道での方位角変化

        cc_tmp = self.ci.circular_curve(Rtmp*phi_circular,\
                                   Rtmp,\
                                   tc1_tmp[1]+phiA,\
                                   Rtmp*phi_circular) # 円軌道

        phi_tc2 = phiA + tc1_tmp[1] + cc_tmp[1] # 出口側緩和曲線始端の方位角

        return tc1_tmp, tc2_tmp, cc_tmp, phi_circular, phi_tc2
    
    def curvetrack_relocation (self,A,phiA,B,phiB,lenTC1,lenTC2,tranfunc,R,dx=0.1,error=0.01):
        ''' A,Bを通る直線を結ぶ曲線軌道の始点を返す
        A:        始点座標
        phiA:     始点での軌道方位
        B:        終点座標
        phiB:     終点での軌道方位
        lenTC1:   始点側の緩和曲線長さ
        lenTC2:   終点側の緩和曲線長さ
        tranfunc: 逓減関数 'line' or 'sin'
        R:        曲線半径
        dx:       残差の微分で使う
        error:    許容誤差
        '''

        def func_TC(Rtmp,lenTC1,lenTC2,A,B,phiA,phiB,x):
            tc1_tmp, tc2_tmp, cc_tmp, phi_circular, phi_tc2 = self.temporal_trackparam(Rtmp,lenTC1,lenTC2,A,B,phiA,phiB,tranfunc)
            
            res_tmp = A+np.array([np.cos(phiA),np.sin(phiA)])*x + tc1_tmp[0] + cc_tmp[0] + np.dot(self.ci.rotate(phi_tc2),tc2_tmp[0]) # 与えられたR, lenTC, delta_phiから計算した着点座標

            # 点Bを通る直線の一般形 ax+by+c=0
            a = -np.tan(phiB)
            b = 1
            c = - a*B[0] - B[1]
            residual = np.abs(a*res_tmp[0]+b*res_tmp[1]+c)/np.sqrt(a**2+b**2) # 点res_tmpと点Bを通る直線の距離

            return (res_tmp,residual)
        
        # 点Bを通る直線（x軸との交差角phiB）との距離が最小になる曲線始点をニュートン法で求める
        num=0 # 繰り返し回数
        f1 = (np.array([0,0]),error*100)
        x =0
        while (f1[1] > error and num<1e3):
            f1 = func_TC(R,lenTC1,lenTC2,A,B,phiA,phiB,x)
            df = (func_TC(R,lenTC1,lenTC2,A,B,phiA,phiB,x+dx)[1]-func_TC(R,lenTC1,lenTC2,A,B,phiA,phiB,x)[1])/dx

            x = x - f1[1]/df
            num +=1
        return (x,f1,num)
    def curvetrack_fit (self,A,phiA,B,phiB,lenTC1,lenTC2,tranfunc,Rtmp=1000,dr=0.1,error=0.01):
        ''' AB間を結ぶ曲線軌道の半径を返す
        A:        始点座標
        phiA:     始点での軌道方位
        B:        終点座標
        phiB:     終点での軌道方位
        lenTC1:   始点側の緩和曲線長さ
        lenTC2:   終点側の緩和曲線長さ
        tranfunc: 逓減関数 'line' or 'sin'
        Rtmp:     曲線半径初期値
        dr:       残差の微分で使う
        error:    許容誤差
        '''

        def func_TC(Rtmp,lenTC1,lenTC2,A,B,phiA,phiB):
            tc1_tmp, tc2_tmp, cc_tmp, phi_circular, phi_tc2 = self.temporal_trackparam(Rtmp,lenTC1,lenTC2,A,B,phiA,phiB,tranfunc)

            res_tmp = A + tc1_tmp[0] + cc_tmp[0] + np.dot(self.ci.rotate(phi_tc2),tc2_tmp[0]) # 与えられたR, lenTC, delta_phiから計算した着点座標

            # 点Bを通る直線の一般形 ax+by+c=0
            a = -np.tan(phiB)
            b = 1
            c = - a*B[0] - B[1]
            residual = np.abs(a*res_tmp[0]+b*res_tmp[1]+c)/np.sqrt(a**2+b**2) # 点res_tmpと点Bを通る直線の距離

            return (res_tmp,residual)
        
        # 点Bを通る直線（x軸との交差角phiB）との距離が最小になる曲線半径をニュートン法で求める
        num=0 # 繰り返し回数
        f1 = (np.array([0,0]),error*100)
        while (f1[1] > error and num<1e3):
            f1 = func_TC(Rtmp,lenTC1,lenTC2,A,B,phiA,phiB)
            df = (func_TC(Rtmp+dr,lenTC1,lenTC2,A,B,phiA,phiB)[1]-func_TC(Rtmp,lenTC1,lenTC2,A,B,phiA,phiB)[1])/dr

            Rtmp = Rtmp - f1[1]/df
            num +=1
        return (Rtmp,f1,num)
    def shift_by_TCL(self,A,phiA,B,phiB,C,tranfunc,TCLtmp=0,dl=0.1,error=0.001):
        ''' AB間を結び、Cに最も近い点を通過する曲線軌道の半径、TCL, CCLを返す。
        始点: A、終点: Bの延長線上となる曲線軌道について、点Cとの距離が最小となるR, TCLをニュートン法で求める。
        A:        始点座標
        phiA:     始点での軌道方位
        B:        終点座標
        phiB:     終点での軌道方位
        C:        経由点
        tranfunc: 逓減関数 'line' or 'sin'
        TCLtmp:   緩和曲線長の初期値
        dl:       残差の微分で使う
        error:    許容誤差
        '''
        def func(lenTC,A,B,phiA,phiB,C,tranfunc):
           Rtmp, f1, num = self.curvetrack_fit(A,phiA,B,phiB,lenTC,lenTC,tranfunc)
           ctplot = curvetrackplot.trackplot()
           ctplot.generate(A,phiA,phiB,Rtmp,lenTC,lenTC,tranfunc)
           mindist, crosspt, min_ix, second_min_ix = math.minimumdist(ctplot.result, C)
           ccl = ctplot.ccl(A,phiA,phiB,Rtmp,lenTC,lenTC,tranfunc)[0]
           return (mindist, ccl, Rtmp)

        # 点Cが円軌道の内側かどうか判断するため、円軌道の中心点を求める
        circular_tr = func(0,A,B,phiA,phiB,C,tranfunc)
        origin_pt = A + np.array([np.cos(phiA+np.pi/2),np.sin(phiA+np.pi/2)])*circular_tr[2]
        len_OC = np.linalg.norm(C - origin_pt)

        # 点Cが円軌道の内側にある場合のエラー処理
        if abs(len_OC) <= abs(circular_tr[2]):
            raise Exception('Unreachable waypoint.\n ({:.1f}, {:.1f})'.format(C[0],C[1]))
        # 点Cとの距離が最小となる軌道のTCLをニュートン法で求める
        num = 0
        f1 = (error*100, 1000, 1000)
        transCL = TCLtmp

        while (f1[0] > error and num<20):
           f1 = func(transCL,A,B,phiA,phiB,C,tranfunc)
           df = (func(transCL+dl,A,B,phiA,phiB,C,tranfunc)[0]-func(transCL,A,B,phiA,phiB,C,tranfunc)[0])/dl

           transCL = transCL - f1[0]/df
           num +=1

        # 求めたTCL, CCL, Rが異常な値をとる場合、CCL=0となるTCLをニュートン法で求めるモードに切り替える
        if transCL < 0 or f1[1] < 0 or np.isnan(transCL) or np.isnan(f1[1]) or np.isnan(f1[2]):
            #print('CCL=0 mode')
            num = 0
            f1 =  (1000, error*100, 1000)
            transCL = TCLtmp

            while (abs(f1[1]) > error and num<20):
               f1 = func(transCL,A,B,phiA,phiB,C,tranfunc)
               df = (func(transCL+dl,A,B,phiA,phiB,C,tranfunc)[1]-func(transCL,A,B,phiA,phiB,C,tranfunc)[1])/dl

               transCL = transCL - f1[1]/df
               num +=1
            
        return (transCL,f1,num)
