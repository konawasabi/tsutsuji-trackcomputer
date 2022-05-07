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

import configparser
import pathlib

class Config():
    def __init__(self,path):
        cp = configparser.ConfigParser()
        cp.read(path)
        self.path_parent = pathlib.Path(path).resolve().parent
        sections = cp.sections()
        self.track_keys = [i for i in sections if i != '@TSUTSUJI_GENERAL']
        
        self.general = {'origin_distance':0, 'offset_variable':None, 'unit_length':1, 'owntrack':None, 'output_path':'./result', 'backimg':None}
        if '@TSUTSUJI_GENERAL' in sections:
            for k in cp.options('@TSUTSUJI_GENERAL'):
                self.general[k] = cp['@TSUTSUJI_GENERAL'][k] if k not in ['origin_distance', 'unit_length'] else float(cp['@TSUTSUJI_GENERAL'][k])
            self.owntrack = self.general['owntrack']
            self.general['output_path'] = self.path_parent.joinpath(pathlib.Path(self.general['output_path']))
            if self.general['backimg'] is not None:
                self.general['backimg'] = self.path_parent.joinpath(pathlib.Path(self.general['backimg']))
        self.track_data = {}
        linecolor_default = ['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd','#8c564b','#e377c2','#7f7f7f','#bcbd22','#17becf']
        color_ix = 0
        for tk in self.track_keys:
            self.track_data[tk] = {'absolute_coordinate':True,\
                                    'x':0,\
                                    'y':0,\
                                    'z':0,\
                                    'angle':0,\
                                    'endpoint':0,\
                                    'file':None,\
                                    'parent_track':None,\
                                    'origin_kilopost':None,\
                                    'isowntrack':False,\
                                    'supplemental_cp':[],\
                                    'color':linecolor_default[color_ix%10]}
            for k in cp.options(tk):
                if k.lower() == 'file':
                    self.track_data[tk][k] = self.path_parent.joinpath(pathlib.Path(cp[tk][k]))
                elif k.lower() in ['x','y','z','angle','endpoint','origin_kilopost']:
                    self.track_data[tk][k] = float(cp[tk][k])
                elif k.lower() in ['isowntrack','absolute_coordinate']:
                    self.track_data[tk][k] = True if cp[tk][k].lower() == 'true' else False
                elif k.lower() in ['supplemental_cp']:
                    for supcp in cp[tk][k].split(','):
                        self.track_data[tk][k].append(float(supcp))
                else:
                    self.track_data[tk][k] = cp[tk][k]
            if self.track_data[tk]['isowntrack']:
                self.owntrack = tk
            color_ix +=1

