# python -m tsutsuji.cui で起動
import matplotlib.pyplot as plt
from kobushi import mapinterpreter
from kobushi import trackgenerator

from . import config

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
                                                    x0 = conf.track_data[i]['x'],\
                                                    y0 = conf.track_data[i]['y'],\
                                                    z0 = conf.track_data[i]['z'],\
                                                    theta0 = conf.track_data[i]['angle'])
    track[i]['result'] = track[i]['tgen'].generate_owntrack()

for i in conf.track_keys:
    tmp = track[i]['result']
    plt.plot(tmp[:,1],tmp[:,2],label=i)
    plt.legend()
plt.show()
