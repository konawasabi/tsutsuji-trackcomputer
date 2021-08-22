# python -m tsutsuji.cui で起動
from kobushi import mapinterpreter

from . import config

conf = config.Config('dev/test.cfg')
print(conf.path_parent)
print(conf.general)
print(conf.track_data.keys())
for i in conf.track_data.keys():
    print(i,conf.track_data[i])
