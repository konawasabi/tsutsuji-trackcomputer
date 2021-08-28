# python -m tsutsuji.cui で起動
import matplotlib.pyplot as plt
import numpy as np

from kobushi import mapinterpreter
from kobushi import trackgenerator

from . import config

def rotate(tau1):
    '''２次元回転行列を返す。
    tau1: 回転角度 [rad]
    '''
    return np.array([[np.cos(tau1), -np.sin(tau1)], [np.sin(tau1),  np.cos(tau1)]])

conf = config.Config('dev/test.cfg')
'''
print(conf.path_parent)
print(conf.general)
print(conf.track_keys)
for i in conf.track_keys:
    print(i,conf.track_data[i])
'''

track = {}
for i in conf.track_keys:
    track[i] = {}
    track[i]['interp'] = mapinterpreter.ParseMap(env=None,parser=None)
    track[i]['data'] = track[i]['interp'].load_files(conf.track_data[i]['file'])
    track[i]['data'].cp_arbdistribution = [min(track[i]['data'].controlpoints.list_cp),\
                                            conf.track_data[i]['endpoint'],\
                                            conf.general['resolution']]
    track[i]['tgen'] = trackgenerator.TrackGenerator(track[i]['data'],\
                                                    x0 = conf.track_data[i]['z'],\
                                                    y0 = conf.track_data[i]['x'],\
                                                    z0 = conf.track_data[i]['y'],\
                                                    theta0 = conf.track_data[i]['angle'])
    track[i]['result'] = track[i]['tgen'].generate_owntrack()

fig = plt.figure()
ax = fig.add_subplot(311)
ax2 = fig.add_subplot(312)
ax3 = fig.add_subplot(313)
for i in conf.track_keys:
    tmp = track[i]['result']
    ax.plot(tmp[:,1],tmp[:,2],label=i)
    
rel_track = {}
for tr in [i for i in conf.track_keys if i != conf.owntrack]:
    tgt = track[tr]['result']
    src = track[conf.owntrack]['result']
    rel_track[tr] = []
    for pos in src:
        tgt_xy = np.vstack((tgt[:,1],tgt[:,2]))
        tgt_xy_trans = np.dot(rotate(-pos[4]),(tgt_xy - np.vstack((pos[1],pos[2])) ) )
        min_ix = np.where(np.abs(tgt_xy_trans[0])==min(np.abs(tgt_xy_trans[0])))
        rel_track[tr].append([pos[0], tgt_xy_trans[0][min_ix][0],tgt_xy_trans[1][min_ix][0]])
    rel_track[tr]=np.array(rel_track[tr])
    print(rel_track[tr])
    ax2.plot(rel_track[tr][:,0],rel_track[tr][:,2],label=tr)
    ax3.plot(rel_track[tr][:,0],rel_track[tr][:,1],label=tr)
ax.legend()
ax2.legend()
ax3.legend()
ax.invert_yaxis()
plt.show()
