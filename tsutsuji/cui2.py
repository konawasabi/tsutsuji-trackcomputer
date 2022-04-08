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

''' python -m tsutsuji.cui2 で起動
'''

import matplotlib.pyplot as plt
import numpy as np
import sys

from kobushi import mapinterpreter
from kobushi import trackgenerator

from . import config
from . import math
from . import track_control

tc = track_control.TrackControl()
tc.loadcfg('dev/test.cfg' if len(sys.argv)==1 else sys.argv[1])
tc.loadmap()
tc.relativepoint_all()
tc.relativeradius()
tc.relativeradius_cp()

fig = plt.figure()
ax = fig.add_subplot(411)
ax2 = fig.add_subplot(412)
ax3 = fig.add_subplot(413)
ax4 = fig.add_subplot(414)

for i in tc.conf.track_keys:
    tmp = tc.track[i]['result']
    ax.plot(tmp[:,1],tmp[:,2],label=i)
for tr in [i for i in tc.conf.track_keys if i != tc.conf.owntrack]:
    ax2.plot(tc.rel_track[tr][:,0],tc.rel_track[tr][:,2],label=tr)
    ax3.plot(tc.rel_track_radius[tr][:,0],tc.rel_track_radius[tr][:,1],label=tr)
    ax4.plot(tc.rel_track_radius[tr][:,0],tc.rel_track_radius[tr][:,2],label=tr)

    ax3.scatter(tc.rel_track_radius_cp[tr][:,0],tc.rel_track_radius_cp[tr][:,1],label=tr,marker='x')
    ax4.scatter(tc.rel_track_radius_cp[tr][:,0],tc.rel_track_radius_cp[tr][:,2],label=tr,marker='x')

    for data in tc.rel_track_radius_cp[tr]:
        print('{:.2f};'.format(data[0]))
        print('Track[\''+tr+'\'].X.Interpolate({:.2f},{:.2f});'.format(data[3],data[2]))

ax.legend()
ax2.legend()
ax3.legend()
ax4.legend()

ax.set_ylabel('abs. pos. [m]')
ax2.set_ylabel('rel. x pos. [m]')
ax3.set_ylabel('curvature [m$^{-1}$]')
ax4.set_ylabel('radius [m]')
ax.invert_yaxis()
plt.show()
