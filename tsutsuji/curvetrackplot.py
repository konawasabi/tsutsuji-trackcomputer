#
#    Copyright 2022-2023 konawasabi
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

from kobushi import trackcoordinate

from . import math

class trackplot():
    def __init__(self):
        self.curvegen = trackcoordinate.curve()
        self.result=np.array([[0,0]])
    def generate(self,A,phiA,phiB,Radius,lenTC1,lenTC2,tranfunc,R0=0):
        delta_phi = math.angle_twov(phiA,phiB) #曲線前後での方位変化
        
        if(lenTC1>0):
            tc1_tmp = self.curvegen.transition_curve(lenTC1,\
                                          R0,\
                                          Radius,\
                                          0,\
                                          tranfunc,n=10) # 入口側の緩和曲線
        else:
            tc1_tmp=(np.array([[0,0]]),0,0)
            
        if(lenTC2>0):
            tc2_tmp = self.curvegen.transition_curve(lenTC2,\
                                          Radius,\
                                          0,\
                                          0,\
                                          tranfunc,n=10) # 出口側の緩和曲線
        else:
            tc2_tmp=(np.array([[0,0]]),0,0)

        phi_circular = delta_phi - tc1_tmp[1] - tc2_tmp[1] # 円軌道での方位角変化
        
        cc_tmp = self.curvegen.circular_curve(Radius*phi_circular,\
                                   Radius,\
                                   tc1_tmp[1]) # 円軌道

        phi_tc2 = tc1_tmp[1] + cc_tmp[1] # 出口側緩和曲線始端の方位角
        
        self.result = np.vstack((np.array([0,0]),tc1_tmp[0]))
        self.result = np.vstack((self.result,self.result[-1] + cc_tmp[0]))
        self.result = np.vstack((self.result,self.result[-1] + np.dot(self.curvegen.rotate(phi_tc2), tc2_tmp[0].T).T))
        
        self.result = np.dot(self.curvegen.rotate(phiA), self.result.T).T
        self.result += A
    def generate_add(self,A,phiA,phiB,Radius,lenTC1,lenTC2,tranfunc,R0=0):
        delta_phi = math.angle_twov(phiA,phiB) #曲線前後での方位変化
        
        if(lenTC1>0):
            tc1_tmp = self.curvegen.transition_curve(lenTC1,\
                                          R0,\
                                          Radius,\
                                          0,\
                                          tranfunc,n=10) # 入口側の緩和曲線
        else:
            tc1_tmp=(np.array([[0,0]]),0,0)
            
        if(lenTC2>0):
            tc2_tmp = self.curvegen.transition_curve(lenTC2,\
                                          Radius,\
                                          0,\
                                          0,\
                                          tranfunc,n=10) # 出口側の緩和曲線
        else:
            tc2_tmp=(np.array([[0,0]]),0,0)

        phi_circular = delta_phi - tc1_tmp[1] - tc2_tmp[1] # 円軌道での方位角変化
        
        cc_tmp = self.curvegen.circular_curve(Radius*phi_circular,\
                                   Radius,\
                                   tc1_tmp[1]) # 円軌道

        phi_tc2 = tc1_tmp[1] + cc_tmp[1] # 出口側緩和曲線始端の方位角
        
        result_tmp = np.vstack((np.array([0,0]),tc1_tmp[0]))
        result_tmp = np.vstack((result_tmp,result_tmp[-1] + cc_tmp[0]))
        result_tmp = np.vstack((result_tmp,result_tmp[-1] + np.dot(self.curvegen.rotate(phi_tc2), tc2_tmp[0].T).T))
        
        result_tmp = np.dot(self.curvegen.rotate(phiA), result_tmp.T).T
        result_tmp += A

        self.result = np.vstack((self.result,result_tmp))
    def ccl(self,A,phiA,phiB,Radius,lenTC1,lenTC2,tranfunc,R0=0):
        ''' 円軌道の長さ(CCL), 円軌道での方位角変化を求める
        '''
        delta_phi = math.angle_twov(phiA,phiB) #曲線前後での方位変化
        
        if(lenTC1>0):
            tc1_tmp = self.curvegen.transition_curve(lenTC1,\
                                          R0,\
                                          Radius,\
                                          0,\
                                          tranfunc) # 入口側の緩和曲線
        else:
            tc1_tmp=(np.array([[0,0]]),0,0)
            
        if(lenTC2>0):
            tc2_tmp = self.curvegen.transition_curve(lenTC2,\
                                          Radius,\
                                          0,\
                                          0,\
                                          tranfunc) # 出口側の緩和曲線
        else:
            tc2_tmp=(np.array([[0,0]]),0,0)

        phi_circul = delta_phi - tc1_tmp[1] - tc2_tmp[1] # 円軌道での方位角変化
        return (Radius*phi_circul, phi_circul)
    def phi_TC(self,lenTC1, Radius, tranfunc, R0=0):
        if lenTC1>0:
            tc1_tmp = self.curvegen.transition_curve(lenTC1,\
                                              R0,\
                                              Radius,\
                                              0,\
                                              tranfunc) # 入口側の緩和曲線
        else:
            tc1_tmp=(np.array([[0,0]]),0,0)    
        return tc1_tmp[1]
