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

import numpy as np

def minimundist(x,y,p):
    track = np.vstack((x,y)).T
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

        if crosspt[0]< track[min_ix][0] or crosspt[0]> track[second_min_ix][0]:
            second_min_ix = min_ix - 1

            lenAC = np.sqrt((track[min_ix][0] - track[second_min_ix][0])**2+(track[min_ix][1] - track[second_min_ix][1])**2)
            n = np.array([(track[min_ix][0] - track[second_min_ix][0])/lenAC,(track[min_ix][1] - track[second_min_ix][1])/lenAC])
            a = np.array([track[second_min_ix][0],track[second_min_ix][1]])

            alpha = -np.dot(a-p,n)    
            mindist = (np.linalg.norm(a-p+alpha*n))
            crosspt = (a+alpha*n)

        #print(track[min_ix],track[second_min_ix])
    else:
        mindist=(distance(dist,min_ix))
        crosspt=(track[min_ix])

    return mindist, crosspt
