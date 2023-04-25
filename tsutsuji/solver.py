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
from kobushi import trackcoordinate as tc
from . import math
from . import curvetrackplot

class solver():
    def __init__(self):
        self.ci = tc.curve_intermediate()
        self.cgen = tc.curve()
    def temporal_trackparam(self,Rtmp,lenTC1,lenTC2,A,B,phiA,phiB,tranfunc,R0=0):
        delta_phi = math.angle_twov(phiA,phiB) #曲線前後での方位変化
            
        if(lenTC1>0):
            tc1_tmp = self.ci.transition_curve(lenTC1,\
                                          R0,\
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
    def curvetrack_fit (self,A,phiA,B,phiB,lenTC1,lenTC2,tranfunc,Rtmp=1000,dr=0.1,error=0.01,R0=0):
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

        R0:       始点での軌道半径（複合曲線の緩和曲線を求める際に使用, default: 0）
        '''

        def func_TC(Rtmp,lenTC1,lenTC2,A,B,phiA,phiB,R0):
            tc1_tmp, tc2_tmp, cc_tmp, phi_circular, phi_tc2 = self.temporal_trackparam(Rtmp,lenTC1,lenTC2,A,B,phiA,phiB,tranfunc,R0=R0)

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
            f1 = func_TC(Rtmp,lenTC1,lenTC2,A,B,phiA,phiB,R0)
            df = (func_TC(Rtmp+dr,lenTC1,lenTC2,A,B,phiA,phiB,R0)[1]-func_TC(Rtmp,lenTC1,lenTC2,A,B,phiA,phiB,R0)[1])/dr

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
    def reverse_curve(self,A,phiA,B,phiB,lenTC11,lenTC12,lenTC21,lenTC22,tranfunc,len_interm=0,C=None,R1=None,R2=None,lenCC1=None,lenCC2=None):
        '''
        [A]-TC-CC-TC-[C]-S-TC-CC-TC-[B]
        '''
        if C is None:
            C = (A + B)/2

        phiC = 2*np.arccos(np.dot(np.array([np.cos(phiA),np.sin(phiA)]), (C-A)/np.linalg.norm(C-A))) + phiA
        
        result_1st = self.curvetrack_fit(A, phiA, C, phiC, lenTC11, lenTC12, tranfunc)
        Cdash = result_1st[1][0] + np.array([np.cos(phiC),np.sin(phiC)])*len_interm

        result_2nd = self.curvetrack_fit(Cdash, phiC, B, phiB, lenTC21, lenTC22, tranfunc)
        return (result_1st,result_2nd,C,Cdash,phiC)
    def compound_curve(self,A,phiA,B,phiB,C,phiC,lenTC1,lenTC2,lenTC3,tranfunc,dl=0.1,error=0.01):
        '''
        [A]-TC-CC-[C]-CC-TC-CC-TC-[B]
        '''
        def func(R1,CCL1tmp,A,phiA,B,phiB,C,lenTC1,lenTC2,lenTC3,tranfunc):
            # [A]-TC1-CC1-TC2-CC2-TC3-[B]なる複合曲線において、CC1の長さをCCL1tmpで与えた場合の着点座標を求める
            # CC1終点座標,方位を求める
            if(lenTC1>0):
                tc1_tmp = self.ci.transition_curve(lenTC1,\
                                              0,\
                                              R1,\
                                              phiA,\
                                              tranfunc,\
                                              lenTC1) # 入口側の緩和曲線
            else:
                tc1_tmp=(np.array([0,0]),0,0)
            cc_tmp = self.ci.circular_curve(CCL1tmp,\
                                            R1,\
                                            tc1_tmp[1]+phiA,\
                                            CCL1tmp) # 円軌道

            CC1end = [A + tc1_tmp[0] + cc_tmp[0], phiA + tc1_tmp[1] + cc_tmp[1]]

            
            # 求めた曲線CC1と点Cの最短距離を求める
            cc_tmp_array = self.cgen.circular_curve(CCL1tmp,\
                                                    R1,\
                                                    tc1_tmp[1]+phiA,\
                                                    n=20)[0] # 円軌道
            cc_tmp_array += A + tc1_tmp[0]
            residual = min(np.linalg.norm(cc_tmp_array-C,axis=1))
            

            # CC1endを始点、Bの延長線上を終点とする単円軌道を求める
            TC3end = self.curvetrack_fit(CC1end[0], CC1end[1], B, phiB, lenTC2, lenTC3, tranfunc, R0=R1)

            # 点TC3endと点Bの距離
            residual = (np.linalg.norm(TC3end[1][0]-B))
            
            return (residual, CC1end, TC3end)

        # 点Aを始点、点Cの延長線上を通過する単円軌道の半径を求める
        result_R1 = self.curvetrack_fit(A, phiA, C, phiC, lenTC1, 0, tranfunc)

        # 点Bを通る直線（x軸との交差角phiB）との距離が最小になる曲線長CCL1をニュートン法で求める
        num=0 # 繰り返し回数
        f1 = (error*100,None,None)
        CCL1 = 100
        while (f1[0] > error and num<1e2):
            f1 =  func(result_R1[0],CCL1,   A,phiA,B,phiB,C,lenTC1,lenTC2,lenTC3,tranfunc)
            df = (func(result_R1[0],CCL1+dl,A,phiA,B,phiB,C,lenTC1,lenTC2,lenTC3,tranfunc)[0]\
                 -func(result_R1[0],CCL1,   A,phiA,B,phiB,C,lenTC1,lenTC2,lenTC3,tranfunc)[0])/dl

            CCL1 = CCL1 - f1[0]/df
            num +=1

        '''returns: 
           CCL1
           f1
              residual
              CC1end
              TC3end
           num
           result_r1
        '''
        return (CCL1,f1,num,result_R1)
    def compound_curve_givenR(self,A,phiA,B,phiB,lenTC1,lenTC2,lenTC3,R1,R2,tranfunc,dphi=0.001,error=0.01):
        def func(phiCC1,A,phiA,B,phiB,lenTC1,lenTC2,lenTC3,R1,R2,tranfunc):
            #delta_phi = math.angle_twov(phiA,phiB) #曲線前後での方位変化
            
            if(lenTC1>0):
                tc1_tmp = self.ci.transition_curve(lenTC1,\
                                              0,\
                                              R1,\
                                              phiA,\
                                              tranfunc,\
                                              lenTC1) # 入口側の緩和曲線
            else:
                tc1_tmp=(np.array([0,0]),0,0)

            #phi_circular = delta_phi - tc1_tmp[1]-tc2_tmp[1] # 円軌道での方位角変化

            cc1_tmp = self.ci.circular_curve(R1*phiCC1,\
                                            R1,\
                                            tc1_tmp[1]+phiA,\
                                            R1*phiCC1) # 円軌道

            if(lenTC2>0):
                tc2_tmp = self.ci.transition_curve(lenTC2,\
                                              R1,\
                                              R2,\
                                              cc1_tmp[1]+tc1_tmp[1]+phiA,\
                                              tranfunc,\
                                              lenTC2) # 出口側の緩和曲線
            else:
                tc2_tmp=(np.array([0,0]),0,0)
                
            if(lenTC3>0):
                tc3_tmp = self.ci.transition_curve(lenTC3,\
                                                   R2,\
                                                   0,\
                                                   0,\
                                                   tranfunc,\
                                                   lenTC3) # 出口側の緩和曲線
            else:
                tc3_tmp=(np.array([0,0]),0,0)

            if (math.angle_twov(phiA,phiB) - (tc1_tmp[1] + tc2_tmp[1] + tc3_tmp[1]))<0:
                raise Exception('invalid R1,R2 pair or too long TC1,2,3')

            phiCC2 = math.angle_twov(phiA,phiB) - (tc1_tmp[1] + tc2_tmp[1] + tc3_tmp[1]) - phiCC1

            cc2_tmp = self.ci.circular_curve(R2*phiCC2,\
                                             R2,\
                                             tc2_tmp[1]+cc1_tmp[1]+tc1_tmp[1]+phiA,\
                                             R2*phiCC2) # 円軌道

            res_tmp = A + tc1_tmp[0] + cc1_tmp[0] + tc2_tmp[0] + cc2_tmp[0] + np.dot(self.ci.rotate(phiCC2+tc2_tmp[1]+phiCC1+tc1_tmp[1]+phiA),tc3_tmp[0])

            # 点Bを通る直線の一般形 ax+by+c=0
            a = -np.tan(phiB)
            b = 1
            c = - a*B[0] - B[1]
            residual = np.abs(a*res_tmp[0]+b*res_tmp[1]+c)/np.sqrt(a**2+b**2) # 点res_tmpと点Bを通る直線の距離
        
            return (res_tmp,residual,tc1_tmp,tc2_tmp,tc3_tmp,cc1_tmp,cc2_tmp,phiCC2)
        # 点Bを通る直線（x軸との交差角phiB）との距離が最小になる曲線始点をニュートン法で求める
        num=0 # 繰り返し回数
        f1 = (np.array([0,0]),error*100)
        phiCC1 = 0.5
        while (f1[1] > error and num<1e2):
            f1 = func(phiCC1,A,phiA,B,phiB,lenTC1,lenTC2,lenTC3,R1,R2,tranfunc)
            df =  (func(phiCC1+dphi,A,phiA,B,phiB,lenTC1,lenTC2,lenTC3,R1,R2,tranfunc)[1]\
                  -func(phiCC1,     A,phiA,B,phiB,lenTC1,lenTC2,lenTC3,R1,R2,tranfunc)[1])/dphi

            phiCC1 = phiCC1 - f1[1]/df
            if phiCC1 * R1 < 0 or f1[7] * R2 < 0:
                raise Exception('invalid R1,R2 pair')
            num +=1
        return (phiCC1,f1,num)        

class IF():
    def __init__(self,A,B,C,phiA,phiB,phiC,lenTC1,lenTC2,lenTC3,lenTC4,lenCC,lenLint,R_input,R2_input,tranfunc,fitmode,curve_fitmode_box,cursor_obj,cursor_f_name,cursor_t_name,cursor_via_name):
        self.trackp = curvetrackplot.trackplot()
        self.sv = solver()
        
        self.A = A
        self.B = B
        self.C = C
        self.phiA = phiA
        self.phiB = phiB
        self.phiC = phiC
        self.lenTC1 = lenTC1
        self.lenTC2 = lenTC2
        self.lenTC3 = lenTC3
        self.lenTC4 = lenTC4
        self.lenCC = lenCC
        self.lenLint = lenLint
        self.R_input = R_input
        self.R2_input = R2_input
        self.tranfunc = tranfunc
        self.fitmode = fitmode
        self.curve_fitmode_box = curve_fitmode_box
        self.cursor_obj = cursor_obj
        self.cursor_f_name = cursor_f_name
        self.cursor_t_name = cursor_t_name
        self.cursor_via_name = cursor_via_name

        self.cursor_f = self.cursor_obj[self.cursor_f_name]
        self.cursor_t = self.cursor_obj[self.cursor_t_name]
        self.cursor_via = self.cursor_obj[self.cursor_via_name]
    def mode1(self):
        parameter_str = ''
        syntax_str = ''
        
        self.result = self.sv.curvetrack_fit(self.A,self.phiA,self.B,self.phiB,self.lenTC1,self.lenTC2,self.tranfunc)
        self.trackp.generate(self.A,self.phiA,self.phiB,self.result[0],self.lenTC1,self.lenTC2,self.tranfunc)
        self.R_result = self.result[0]
        self.CCL_result = self.trackp.ccl(self.A,self.phiA,self.phiB,self.result[0],self.lenTC1,self.lenTC2,self.tranfunc)[0]
        self.shift_result = np.linalg.norm(self.result[1][0] - self.B)*np.sign(np.dot(np.array([np.cos(self.phiB),np.sin(self.phiB)]),self.result[1][0] - self.B))

        parameter_str += self.gen_paramstr_mode1_2()
        syntax_str += self.generate_mapsyntax()

        return {'track':self.trackp.result, 'param':parameter_str, 'syntax':syntax_str}
    def mode2(self):
        parameter_str = ''
        syntax_str = ''
        
        phiA_inv = self.phiA - np.pi if self.phiA>0 else self.phiA + np.pi
        phiB_inv = self.phiB - np.pi if self.phiB>0 else self.phiB + np.pi
        self.result = self.sv.curvetrack_fit(self.B,phiB_inv,self.A,phiA_inv,self.lenTC2,self.lenTC1,self.tranfunc)
        self.trackp.generate(self.B,phiB_inv,phiA_inv,self.result[0],self.lenTC2,self.lenTC1,self.tranfunc)
        self.R_result = -self.result[0]
        self.CCL_result = self.trackp.ccl(self.B,phiB_inv,phiA_inv,self.result[0],self.lenTC1,self.lenTC2,self.tranfunc)[0]
        self.shift_result = np.linalg.norm(self.result[1][0] - self.A)*np.sign(np.dot(np.array([np.cos(self.phiA),np.sin(self.phiA)]),self.result[1][0] - self.A))

        parameter_str += self.gen_paramstr_mode1_2()
        syntax_str += self.generate_mapsyntax()

        return {'track':self.trackp.result, 'param':parameter_str, 'syntax':syntax_str}
    def mode3(self):
        parameter_str = ''
        syntax_str = ''
        
        self.result = self.sv.curvetrack_relocation(self.A,self.phiA,self.B,self.phiB,self.lenTC1,self.lenTC2,self.tranfunc,self.R_input)
        self.A_result = self.A + np.array([np.cos(self.phiA),np.sin(self.phiA)])*self.result[0]
        self.R_result = self.R_input
        self.trackp.generate(self.A_result,self.phiA,self.phiB,self.R_input,self.lenTC1,self.lenTC2,self.tranfunc)
        self.CCL_result = self.trackp.ccl(self.A_result,self.phiA,self.phiB,self.R_input,self.lenTC1,self.lenTC2,self.tranfunc)[0]
        self.shift_result = self.result[0]

        parameter_str += self.gen_paramstr_mode3()
        syntax_str += self.generate_mapsyntax()

        return {'track':self.trackp.result, 'param':parameter_str, 'syntax':syntax_str}
    def mode4_5(self,assigncursor):
        parameter_str = ''
        syntax_str = ''

        if self.fitmode == self.curve_fitmode_box['values'][3]:
            self.phi_end = self.phiA + self.lenCC/self.R_input + self.trackp.phi_TC(self.lenTC1, self.R_input, self.tranfunc) + self.trackp.phi_TC(self.lenTC2, self.R_input, self.tranfunc)
            self.trackp.generate(self.A, self.phiA, self.phi_end, self.R_input, self.lenTC1, self.lenTC2, self.tranfunc)
        else:
            self.phi_end = self.phiB - (self.lenCC/self.R_input + self.trackp.phi_TC(self.lenTC1, self.R_input, self.tranfunc) + self.trackp.phi_TC(self.lenTC2, self.R_input, self.tranfunc))
            self.trackp.generate(self.B, self.phiB + np.pi if self.phiB>0 else self.phiB - np.pi, self.phi_end + np.pi if self.phi_end>0 else self.phi_end - np.pi, -self.R_input, self.lenTC2, self.lenTC1, self.tranfunc)
        self.R_result = self.R_input
        self.CCL_result = self.lenCC
        self.shift_result = 0

        parameter_str += self.gen_paramstr_mode4_5()
        syntax_str += self.generate_mapsyntax()

        if assigncursor:
            if self.fitmode == self.curve_fitmode_box['values'][3]:
                tmp_cursor = self.cursor_t
                tmp_cursor.values[0].set(self.trackp.result[:,0][-1])
                tmp_cursor.values[1].set(self.trackp.result[:,1][-1])
                tmp_cursor.values[2].set(np.rad2deg(self.phi_end))
                tmp_cursor.marker.set_direct()
                tmp_cursor.arrow.set_direct()
            elif self.fitmode == self.curve_fitmode_box['values'][4]:
                tmp_cursor = self.cursor_f
                tmp_cursor.values[0].set(self.trackp.result[:,0][-1])
                tmp_cursor.values[1].set(self.trackp.result[:,1][-1])
                tmp_cursor.values[2].set(np.rad2deg(self.phi_end))
                tmp_cursor.marker.set_direct()
                tmp_cursor.arrow.set_direct()

        return {'track':self.trackp.result, 'param':parameter_str, 'syntax':syntax_str}
    def mode6(self):
        parameter_str = ''
        syntax_str = ''

        self.result = self.sv.shift_by_TCL(self.A,self.phiA,self.B,self.phiB,self.C,self.tranfunc)
        self.trackp.generate(self.A,self.phiA,self.phiB,self.result[1][2],self.result[0],self.result[0],self.tranfunc)
        self.R_result = self.result[1][2]
        self.CCL_result = self.result[1][1]
        self.TCL_result = self.result[0]
        self.endpoint = self.trackp.result[-1]
        self.shift_result = np.linalg.norm(self.endpoint - self.B)*np.sign(np.dot(np.array([np.cos(self.phiB),np.sin(self.phiB)]),self.endpoint - self.B))

        parameter_str += self.gen_paramstr_mode6_7()
        syntax_str += self.generate_mapsyntax()
        return {'track':self.trackp.result, 'param':parameter_str, 'syntax':syntax_str}
    def mode7(self):
        parameter_str = ''
        syntax_str = ''

        phiA_inv = self.phiA - np.pi if self.phiA>0 else self.phiA + np.pi
        phiB_inv = self.phiB - np.pi if self.phiB>0 else self.phiB + np.pi
        self.result = self.sv.shift_by_TCL(self.B,phiB_inv,self.A,phiA_inv,self.C,self.tranfunc)
        self.trackp.generate(self.B,phiB_inv,phiA_inv,self.result[1][2],self.result[0],self.result[0],self.tranfunc)
        self.R_result = -self.result[1][2]
        self.CCL_result = self.result[1][1]
        self.TCL_result = self.result[0]
        self.endpoint = self.trackp.result[-1]
        self.shift_result = np.linalg.norm(self.endpoint - self.A)*np.sign(np.dot(np.array([np.cos(self.phiA),np.sin(self.phiA)]),self.endpoint - self.A))

        parameter_str += self.gen_paramstr_mode6_7()
        syntax_str += self.generate_mapsyntax()
        return {'track':self.trackp.result, 'param':parameter_str, 'syntax':syntax_str}
    def mode8(self,withCpos = True):
        parameter_str = ''
        syntax_str = ''
        if withCpos:
            self.result = self.sv.reverse_curve(self.A,self.phiA,self.B,self.phiB,self.lenTC1,self.lenTC2,self.lenTC3,self.lenTC4,self.tranfunc,C=self.C,len_interm=self.lenLint)
        else:
            self.result = self.sv.reverse_curve(self.A,self.phiA,self.B,self.phiB,self.lenTC1,self.lenTC2,self.lenTC3,self.lenTC4,self.tranfunc,len_interm=self.lenLint)

        self.trackp.generate(self.A,self.phiA,self.result[4],self.result[0][0],self.lenTC1,self.lenTC2,self.tranfunc)
        self.trackp.generate_add(self.result[3],self.result[4],self.phiB,self.result[1][0],self.lenTC3,self.lenTC4,self.tranfunc)

        self.CCL_result = self.trackp.ccl(self.A,self.phiA,self.result[4],self.result[0][0],self.lenTC1,self.lenTC2,self.tranfunc)[0]
        self.CCL2_result = self.trackp.ccl(self.result[3],self.result[4],self.phiB,self.result[1][0],self.lenTC3,self.lenTC4,self.tranfunc)[0]
        self.R1_val = self.result[0][0]
        self.R2_val = self.result[1][0]

        self.shift_result = np.linalg.norm(self.result[1][1][0] - self.B)*np.sign(np.dot(np.array([np.cos(self.phiB),np.sin(self.phiB)]),self.result[1][1][0] - self.B))

        parameter_str += self.gen_paramstr_mode8(withCpos=withCpos)
        syntax_str += self.generate_mapsyntax_reversecurve()
        return {'track':self.trackp.result, 'param':parameter_str, 'syntax':syntax_str}
    def mode9(self):
        parameter_str = ''
        syntax_str = ''

        if False:
            import pdb
            pdb.set_trace()

        #phiC = 2*np.arccos(np.dot(np.array([np.cos(self.phiA),np.sin(self.phiA)]), (self.C-self.A)/np.linalg.norm(self.C-self.A))) + self.phiA

        self.result = self.sv.compound_curve(self.A,self.phiA,self.B,self.phiB,self.C,self.phiC,self.lenTC1,self.lenTC2,self.lenTC4,self.tranfunc)

        self.R1_val = self.result[3][0]
        self.R2_val = self.result[1][2][0]
        self.CCL_result = self.result[0]
        self.CCL2_result = self.trackp.ccl(self.result[1][1][0], self.result[1][1][1], self.phiB, self.result[1][2][0], self.lenTC2, self.lenTC4, self.tranfunc, R0 = self.result[3][0])[0]
        self.endpos = self.result[1][2][1][0]
        self.shift_result = np.linalg.norm(self.endpos - self.B)*np.sign(np.dot(np.array([np.cos(self.phiB),np.sin(self.phiB)]),self.endpos - self.B))

        self.trackp.generate(self.A,self.phiA,self.result[1][1][1],self.result[3][0],self.lenTC1,0,self.tranfunc)
        self.trackp.generate_add(self.result[1][1][0], self.result[1][1][1], self.phiB, self.result[1][2][0], self.lenTC2, self.lenTC4, self.tranfunc, R0 = self.result[3][0])

        parameter_str += self.gen_paramstr_mode9()
        syntax_str += self.generate_mapsyntax_compoundcurve()
        
        return {'track':self.trackp.result, 'param':parameter_str, 'syntax':syntax_str}
    def mode10(self):
        parameter_str = ''
        syntax_str = ''

        self.result_R1 = self.sv.curvetrack_relocation(self.A,self.phiA,self.C,self.phiC,self.lenTC1,self.lenTC2,self.tranfunc,self.R_input)

        self.Cdash = self.result_R1[1][0]

        self.result_R2 = self.sv.curvetrack_relocation(self.Cdash,self.phiC,self.B,self.phiB,self.lenTC3,self.lenTC4,self.tranfunc,self.R2_input)

        #intermed_vec = self.Cdash + self.result_R2[0]*np.array([np.cos(self.phiC),np.sin(self.phiC)])
        #self.interm_length = np.linalg.norm(intermed_vec) * np.sign(np.dot(np.array([np.cos(self.phiC),np.sin(self.phiC)]), intermed_vec))

        self.A_result = self.A + self.result_R1[0]*np.array([np.cos(self.phiA),np.sin(self.phiA)])
        self.C_result = self.Cdash + self.result_R2[0]*np.array([np.cos(self.phiC),np.sin(self.phiC)])
        self.CCL_result  = self.trackp.ccl(self.A_result,self.phiA,self.phiC,self.R_input ,self.lenTC1,self.lenTC2,self.tranfunc)[0]
        self.CCL2_result = self.trackp.ccl(self.C_result,self.phiC,self.phiB,self.R2_input,self.lenTC3,self.lenTC4,self.tranfunc)[0]
        self.lenLint = self.result_R2[0]
        self.shift_result = self.result_R1[0]
        self.R1_val = self.R_input
        self.R2_val = self.R2_input

        
        self.trackp.generate(self.A_result,\
                             self.phiA,self.phiC,self.R_input,self.lenTC1,self.lenTC2,self.tranfunc)
        self.trackp.generate_add(self.C_result,\
                             self.phiC,self.phiB,self.R2_input,self.lenTC3,self.lenTC4,self.tranfunc)


        syntax_str = self.generate_mapsyntax_reversecurve(initial_shift = True)
        parameter_str = self.gen_paramstr_mode8(endpos=False)
        
        return {'track':self.trackp.result, 'param':parameter_str, 'syntax':syntax_str}
    def mode11(self):
        parameter_str = ''
        syntax_str = ''
        self.result = self.sv.compound_curve_givenR(self.A,self.phiA,self.B,self.phiB,self.lenTC1,self.lenTC2,self.lenTC4,self.R_input,self.R2_input,self.tranfunc)

        for i in self.result:
            print(i)

        self.trackp.generate(self.A,\
                             self.phiA,self.result[0]+self.result[1][2][1]+self.phiA,self.R_input,self.lenTC1,0,self.tranfunc)
        self.trackp.generate_add(self.A + self.result[1][2][0] + self.result[1][5][0],\
                                 self.result[0]+self.result[1][2][1]+self.phiA,self.phiB,self.R2_input,self.lenTC2,self.lenTC4,self.tranfunc,R0=self.R_input)

        self.R1_val = self.R_input
        self.R2_val = self.R2_input
        self.CCL_result = self.R1_val * self.result[0]
        self.CCL2_result = self.R2_val * self.result[1][6][1]
        self.endpos = self.result[1][0]
        self.shift_result = np.linalg.norm(self.endpos - self.B)*np.sign(np.dot(np.array([np.cos(self.phiB),np.sin(self.phiB)]),self.endpos - self.B))

        syntax_str = self.generate_mapsyntax_compoundcurve()
        parameter_str = self.gen_paramstr_mode9(givenR=True)

        return {'track':self.trackp.result, 'param':parameter_str, 'syntax':syntax_str}
    def generate_mapsyntax(self):
        syntax_str = ''
        syntax_str += '$pt_a = {:f};'.format(self.cursor_f.values[4].get() if self.cursor_f.values[3].get() != '@absolute' else 0) + '\n'
        if self.fitmode == self.curve_fitmode_box['values'][0] or self.fitmode == self.curve_fitmode_box['values'][5]:
            shift = 0
            syntax_str += '$pt_a;' + '\n'
        else:
            shift = self.shift_result
            syntax_str += '$pt_a {:s}{:f};'.format('+' if shift>=0 else '',shift) + '\n'
        syntax_str += '$cant = 0;' + '\n'
        syntax_str += 'Curve.SetFunction({:d});'.format(0 if self.tranfunc == 'sin' else 1) + '\n'
        syntax_str += 'Curve.Interpolate({:f},0);'.format(0) + '\n'
        if self.fitmode == self.curve_fitmode_box['values'][5] or self.fitmode == self.curve_fitmode_box['values'][6]:
            lenTC_result = {'1':self.TCL_result, '2':self.TCL_result}
        else:
            lenTC_result = {'1':self.lenTC1, '2':self.lenTC2}
        if lenTC_result['1'] != 0 or True:
            tmp = shift + lenTC_result['1']
            syntax_str += '$pt_a {:s}{:f};'.format('+' if tmp>=0 else '', tmp) + '\n'
        syntax_str += 'Curve.Interpolate({:f}, $cant);'.format(self.R_result) + '\n'
        tmp = (shift + lenTC_result['1'] + self.CCL_result)
        syntax_str += '$pt_a {:s}{:f};'.format('+' if tmp>=0 else '', tmp) + '\n'
        syntax_str += 'Curve.Interpolate({:f}, $cant);'.format(self.R_result) + '\n'
        if lenTC_result['2'] != 0 or True:
            tmp = (shift + lenTC_result['1'] + self.CCL_result + lenTC_result['2'])
            syntax_str += '$pt_a {:s}{:f};'.format('+' if tmp>=0 else '', tmp) + '\n'
        syntax_str += 'Curve.Interpolate({:f},0);'.format(0) + '\n'
        
        return syntax_str
    def generate_mapsyntax_reversecurve(self,initial_shift=None):
        syntax_str = ''
        syntax_str += '$pt_a = {:f};'.format(self.cursor_f.values[4].get() \
                                             if self.cursor_f.values[3].get() != '@absolute' else 0) + '\n'
        if initial_shift is None:
            shift = 0
            syntax_str += '$pt_a;' + '\n'
        else:
            shift = self.shift_result
            tmp = shift
            syntax_str += '$pt_a {:s}{:f};'.format('+' if tmp>=0 else '', tmp) + '\n'
        syntax_str += '$cant = 0;' + '\n'
        syntax_str += 'Curve.SetFunction({:d});'.format(0 if self.tranfunc == 'sin' else 1) + '\n'
        syntax_str += 'Curve.Interpolate({:f},0);'.format(0) + '\n'
        
        tmp = shift + self.lenTC1
        syntax_str += '$pt_a {:s}{:f};'.format('+' if tmp>=0 else '', tmp) + '\n'
        syntax_str += 'Curve.Interpolate({:f}, $cant);'.format(self.R1_val) + '\n'
        
        tmp = (shift + self.lenTC1 + self.CCL_result)
        syntax_str += '$pt_a {:s}{:f};'.format('+' if tmp>=0 else '', tmp) + '\n'
        syntax_str += 'Curve.Interpolate({:f}, $cant);'.format(self.R1_val) + '\n'
        
        tmp = (shift + self.lenTC1 + self.CCL_result + self.lenTC2)
        syntax_str += '$pt_a {:s}{:f};'.format('+' if tmp>=0 else '', tmp) + '\n'
        syntax_str += 'Curve.Interpolate({:f},0);'.format(0) + '\n'
        syntax_str += '\n'

        end_R1 = shift + self.lenTC1 + self.CCL_result + self.lenTC2 + self.lenLint
        tmp = end_R1
        syntax_str += '$pt_a {:s}{:f};'.format('+' if tmp>=0 else '', tmp) + '\n'
        syntax_str += '$cant = 0;' + '\n'
        syntax_str += 'Curve.Interpolate({:f},0);'.format(0) + '\n'

        tmp = end_R1 + self.lenTC3
        syntax_str += '$pt_a {:s}{:f};'.format('+' if tmp>=0 else '', tmp) + '\n'
        syntax_str += 'Curve.Interpolate({:f}, $cant);'.format(self.R2_val) + '\n'
        
        tmp = (end_R1 + self.lenTC3 + self.CCL2_result)
        syntax_str += '$pt_a {:s}{:f};'.format('+' if tmp>=0 else '', tmp) + '\n'
        syntax_str += 'Curve.Interpolate({:f}, $cant);'.format(self.R2_val) + '\n'
        
        tmp = (end_R1 + self.lenTC3 + self.CCL2_result + self.lenTC4)
        syntax_str += '$pt_a {:s}{:f};'.format('+' if tmp>=0 else '', tmp) + '\n'
        syntax_str += 'Curve.Interpolate({:f},0);'.format(0) + '\n'
        
        return syntax_str
    def generate_mapsyntax_compoundcurve(self):
        syntax_str = ''
        syntax_str += '$pt_a = {:f};'.format(self.cursor_f.values[4].get() \
                                             if self.cursor_f.values[3].get() != '@absolute' else 0) + '\n'
        shift = 0
        syntax_str += '$pt_a;' + '\n'
        syntax_str += '$cant = 0;' + '\n'
        syntax_str += 'Curve.SetFunction({:d});'.format(0 if self.tranfunc == 'sin' else 1) + '\n'
        syntax_str += 'Curve.Interpolate({:f},0);'.format(0) + '\n'
        
        tmp = shift + self.lenTC1
        syntax_str += '$pt_a {:s}{:f};'.format('+' if tmp>=0 else '', tmp) + '\n'
        syntax_str += 'Curve.Interpolate({:f}, $cant);'.format(self.R1_val) + '\n'
        
        tmp = (shift + self.lenTC1 + self.CCL_result)
        syntax_str += '$pt_a {:s}{:f};'.format('+' if tmp>=0 else '', tmp) + '\n'
        syntax_str += 'Curve.Interpolate({:f}, $cant);'.format(self.R1_val) + '\n'

        end_R1 = shift + self.lenTC1 + self.CCL_result + self.lenTC2
        tmp = end_R1
        syntax_str += '$pt_a {:s}{:f};'.format('+' if tmp>=0 else '', tmp) + '\n'
        syntax_str += '$cant = 0;' + '\n'
        syntax_str += 'Curve.Interpolate({:f}, $cant);'.format(self.R2_val) + '\n'
        
        tmp = (end_R1  + self.CCL2_result)
        syntax_str += '$pt_a {:s}{:f};'.format('+' if tmp>=0 else '', tmp) + '\n'
        syntax_str += 'Curve.Interpolate({:f}, $cant);'.format(self.R2_val) + '\n'
        
        tmp = (end_R1  + self.CCL2_result + self.lenTC4)
        syntax_str += '$pt_a {:s}{:f};'.format('+' if tmp>=0 else '', tmp) + '\n'
        syntax_str += 'Curve.Interpolate({:f},0);'.format(0) + '\n'
        
        return syntax_str
    def gen_paramstr_mode1_2(self):
        parameter_str = ''

        parameter_str += '[Curve fitting]\n'
        parameter_str += 'Inputs:\n'
        parameter_str += '   Fitmode:          {:s}\n'.format(self.fitmode)
        parameter_str += '   Cursor α,β:       {:s},{:s}\n'.format(self.cursor_f_name,self.cursor_t_name)
        parameter_str += '   Ponint α:         ({:f}, {:f})\n'.format(self.A[0],self.A[1])
        parameter_str += '   Ponint β:         ({:f}, {:f})\n'.format(self.B[0],self.B[1])
        parameter_str += '   Direction α:     {:f}\n'.format(self.cursor_f.values[2].get())
        parameter_str += '   Direction β:     {:f}\n'.format(self.cursor_t.values[2].get())
        parameter_str += '   Transition func.: {:s}\n'.format(self.tranfunc)
        parameter_str += '   TCL α:            {:f}\n'.format(self.lenTC1)
        parameter_str += '   TCL β:            {:f}\n'.format(self.lenTC2)            
        parameter_str += 'Results:\n'
        parameter_str += '   R:   {:f}\n'.format(self.R_result)
        parameter_str += '   CCL: {:f}\n'.format(self.CCL_result)
        parameter_str += '   endpt:            ({:f}, {:f})\n'.format(self.result[1][0][0],self.result[1][0][1])
        parameter_str += '   shift from pt. β: {:f}\n'.format(self.shift_result)
        if self.fitmode == self.curve_fitmode_box['values'][0]:
            parameter_str += '   endpt:            ({:f}, {:f})'.format(self.result[1][0][0],self.result[1][0][1]) + '\n'
            parameter_str += '   shift from pt. β: {:f}'.format(self.shift_result) + '\n'
        else:
            parameter_str += '   startpt:          ({:f}, {:f})'.format(self.result[1][0][0],self.result[1][0][1]) + '\n'
            parameter_str += '   shift from pt. α: {:f}'.format(self.shift_result) + '\n'

        return parameter_str
    def gen_paramstr_mode3(self):
        parameter_str = ''

        parameter_str += '[Curve fitting]' + '\n'
        parameter_str += 'Inputs:' + '\n'
        parameter_str += '   Fitmode:          {:s}'.format(self.fitmode) + '\n'
        parameter_str += '   Cursor α,β:       {:s},{:s}'.format(self.cursor_f_name,self.cursor_t_name) + '\n'
        parameter_str += '   Ponint α:         ({:f}, {:f})'.format(self.A[0],self.A[1]) + '\n'
        parameter_str += '   Ponint β:         ({:f}, {:f})'.format(self.B[0],self.B[1]) + '\n'
        parameter_str += '   Direction α:     {:f}'.format(self.cursor_f.values[2].get()) + '\n'
        parameter_str += '   Direction β:     {:f}'.format(self.cursor_t.values[2].get()) + '\n'
        parameter_str += '   Transition func.: {:s}'.format(self.tranfunc) + '\n'
        parameter_str += '   TCL α:            {:f}'.format(self.lenTC1) + '\n'
        parameter_str += '   TCL β:            {:f}'.format(self.lenTC2) + '\n'
        parameter_str += '   R:                {:f}'.format(self.R_input) + '\n'
        parameter_str += 'Results:' + '\n'
        parameter_str += '   CCL:        {:f}'.format(self.CCL_result) + '\n'
        parameter_str += '   startpoint: ({:f}, {:f})'.format(self.A_result[0],self.A_result[1]) + '\n'
        parameter_str += '   shift:      {:f}'.format(self.shift_result) + '\n'
        return parameter_str
    def gen_paramstr_mode4_5(self):
        parameter_str = ''
        cursor_label = 'α' if self.fitmode == self.curve_fitmode_box['values'][3] else 'β'
        
        parameter_str += '[Curve fitting]' + '\n'
        parameter_str += 'Inputs:' + '\n'
        parameter_str += '   Fitmode:          {:s}'.format(self.fitmode) + '\n'
        parameter_str += '   Cursor {:s}:         {:s}'.format(cursor_label,self.cursor_f_name) + '\n'
        parameter_str += '   Ponint {:s}:         ({:f}, {:f})'.format(cursor_label,self.A[0],self.A[1]) + '\n'
        parameter_str += '   Direction {:s}:      {:f}'.format(cursor_label,self.cursor_f.values[2].get()) + '\n'
        parameter_str += '   Transition func.: {:s}'.format(self.tranfunc) + '\n'
        parameter_str += '   TCL α:            {:f}'.format(self.lenTC1) + '\n'
        parameter_str += '   TCL β:            {:f}'.format(self.lenTC2) + '\n'
        parameter_str += '   CCL:              {:f}'.format(self.CCL_result) + '\n'
        parameter_str += '   R:                {:f}'.format(self.R_input) + '\n'
        parameter_str += 'Results:' + '\n'
        if self.fitmode == self.curve_fitmode_box['values'][3]:
            parameter_str += '   endpoint: ({:f}, {:f})'.format(self.trackp.result[:,0][-1],self.trackp.result[:,1][-1]) + '\n'
            parameter_str += '   phi_end:  {:f}'.format(np.rad2deg(self.phi_end)) + '\n'

        else:
            parameter_str += '   startpoint: ({:f}, {:f})'.format(self.trackp.result[:,0][-1],self.trackp.result[:,1][-1]) + '\n'
            parameter_str += '   phi_start:  {:f}'.format(np.rad2deg(self.phi_end)) + '\n'
        return parameter_str
    def gen_paramstr_mode6_7(self):
        parameter_str = ''
        parameter_str += '[Curve fitting]' + '\n'
        parameter_str += 'Inputs:' +'\n'
        parameter_str += '   Fitmode:          {:s}'.format(self.fitmode) +'\n'
        parameter_str += '   Cursor α,β,γ:     {:s},{:s},{:s}'.format(self.cursor_f_name,self.cursor_t_name,self.cursor_via_name) +'\n'
        parameter_str += '   Ponint α:         ({:f}, {:f})'.format(self.A[0],self.A[1]) +'\n'
        parameter_str += '   Ponint β:         ({:f}, {:f})'.format(self.B[0],self.B[1]) +'\n'
        parameter_str += '   Ponint γ:         ({:f}, {:f})'.format(self.C[0],self.C[1]) +'\n'
        parameter_str += '   Direction α:     {:f}'.format(self.cursor_f.values[2].get()) +'\n'
        parameter_str += '   Direction β:     {:f}'.format(self.cursor_t.values[2].get()) +'\n'
        parameter_str += '   Transition func.: {:s}'.format(self.tranfunc) +'\n'          
        parameter_str += 'Results:' +'\n'
        parameter_str += '   R:   {:f}'.format(self.R_result) +'\n'
        parameter_str += '   CCL: {:f}'.format(self.CCL_result) +'\n'
        parameter_str += '   TCL: {:f}'.format(self.TCL_result) +'\n'
        if '6.' in self.fitmode:
            #endpoint = self.trackp.result[-1]
            parameter_str += '   endpt:            ({:f}, {:f})'.format(self.endpoint[0],self.endpoint[1]) +'\n'
            parameter_str += '   shift from pt. β: {:f}'.format(self.shift_result) +'\n'
        else:
            parameter_str += '   startpt:          ({:f}, {:f})'.format(self.endpoint[0],self.endpoint[1]) +'\n'
            parameter_str += '   shift from pt. α: {:f}'.format(self.shift_result) +'\n'
        return parameter_str
    def gen_paramstr_mode8(self,withCpos=True,endpos=True):
        parameter_str = ''

        parameter_str += '[Curve fitting]' + '\n'
        parameter_str += 'Inputs:' + '\n'
        parameter_str += '   Fitmode:          {:s}'.format(self.fitmode) + '\n'
        parameter_str += '   Cursor α,β,γ:     {:s},{:s},{:s}'.format(self.cursor_f_name,self.cursor_t_name,self.cursor_via_name) + '\n'
        parameter_str += '   Ponint α:         ({:f}, {:f})'.format(self.A[0],self.A[1]) + '\n'
        parameter_str += '   Ponint β:         ({:f}, {:f})'.format(self.B[0],self.B[1]) + '\n'
        if withCpos:
            parameter_str += '   Ponint γ:         ({:f}, {:f})'.format(self.C[0],self.C[1]) + '\n'
        parameter_str += '   Direction α:      {:f}'.format(self.cursor_f.values[2].get()) + '\n'
        parameter_str += '   Direction β:      {:f}'.format(self.cursor_t.values[2].get()) + '\n'
        parameter_str += '   Transition func.: {:s}'.format(self.tranfunc) + '\n'
        parameter_str += '   TCL1:             {:f}'.format(self.lenTC1) + '\n'
        parameter_str += '   TCL2:             {:f}'.format(self.lenTC2) + '\n'
        parameter_str += '   TCL3:             {:f}'.format(self.lenTC3) + '\n'
        parameter_str += '   TCL4:             {:f}'.format(self.lenTC4) + '\n'
        parameter_str += '   L intermediate:   {:f}'.format(self.lenLint) + '\n'
        parameter_str += 'Results:' + '\n'
        parameter_str += '   R1:        {:f}'.format(self.R1_val) + '\n'
        parameter_str += '   CCL1:      {:f}'.format(self.CCL_result) + '\n'
        parameter_str += '   R2:        {:f}'.format(self.R2_val) + '\n'
        parameter_str += '   CCL2:      {:f}'.format(self.CCL2_result) + '\n'
        if endpos:
            parameter_str += '   endpt:     ({:f}, {:f})\n'.format(self.result[1][1][0][0],self.result[1][1][0][1])
            parameter_str += '   shift from pt. β: {:f}\n'.format(self.shift_result)
        else:
            parameter_str += '   startpt:   ({:f}, {:f})\n'.format(self.A_result[0],self.A_result[1])
            parameter_str += '   shift from pt. α: {:f}\n'.format(self.shift_result)
        return parameter_str
    def gen_paramstr_mode9(self,givenR=False):
        parameter_str = ''

        parameter_str += '[Curve fitting]' + '\n'
        parameter_str += 'Inputs:' + '\n'
        parameter_str += '   Fitmode:          {:s}'.format(self.fitmode) + '\n'
        parameter_str += '   Cursor α,β,γ:     {:s},{:s},{:s}'.format(self.cursor_f_name,self.cursor_t_name,self.cursor_via_name) + '\n'
        parameter_str += '   Ponint α:         ({:f}, {:f})'.format(self.A[0],self.A[1]) + '\n'
        parameter_str += '   Ponint β:         ({:f}, {:f})'.format(self.B[0],self.B[1]) + '\n'
        parameter_str += '   Ponint γ:         ({:f}, {:f})'.format(self.C[0],self.C[1]) + '\n'
        parameter_str += '   Direction α:      {:f}'.format(self.cursor_f.values[2].get()) + '\n'
        parameter_str += '   Direction β:      {:f}'.format(self.cursor_t.values[2].get()) + '\n'
        parameter_str += '   Direction γ:      {:f}'.format(self.cursor_via.values[2].get()) + '\n'
        parameter_str += '   Transition func.: {:s}'.format(self.tranfunc) + '\n'
        parameter_str += '   TCL1:             {:f}'.format(self.lenTC1) + '\n'
        parameter_str += '   TCL2:             {:f}'.format(self.lenTC2) + '\n'
        #parameter_str += '   TCL3:             {:f}'.format(self.lenTC3) + '\n'
        parameter_str += '   TCL4:             {:f}'.format(self.lenTC4) + '\n'
        #parameter_str += '   L intermediate:   {:f}'.format(self.lenLint) + '\n'
        if givenR:
            parameter_str += '   R1:               {:f}'.format(self.R1_val) + '\n'
            parameter_str += '   R2:               {:f}'.format(self.R2_val) + '\n'
        parameter_str += 'Results:' + '\n'
        if givenR is False:
            parameter_str += '   R1:        {:f}'.format(self.R1_val) + '\n'
            parameter_str += '   R2:        {:f}'.format(self.R2_val) + '\n'
        parameter_str += '   CCL1:      {:f}'.format(self.CCL_result) + '\n'
        parameter_str += '   CCL2:      {:f}'.format(self.CCL2_result) + '\n'
        parameter_str += '   endpt:     ({:f}, {:f})\n'.format(self.endpos[0],self.endpos[1])
        parameter_str += '   shift from pt. β: {:f}\n'.format(self.shift_result)
        return parameter_str
