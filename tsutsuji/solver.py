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

class solver():
    def __init__(self):
        self.ci = tc.curve_intermediate()
    
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
            delta_phi = math.angle_twov(phiA,phiB)
            
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
