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
        self.cp = configparser.ConfigParser()

        try:
            self.cp.read(path,'utf-8')
        except UnicodeDecodeError as e:
            print('Warning: {:s} cannot be decoded with utf-8. Tsutsuji tries to decode with CP932.'.format(str(path)))
            try:
                self.cp.read(path,'cp932')
            except UnicodeDecodeError as e:
                raise RuntimeError('Unknown encoding: {:s}'.format(str(path)))

        self.path_parent = pathlib.Path(path).resolve().parent
        sections = self.cp.sections()
        self.track_keys = [i for i in sections if '@' not in i]
        self.kml_keys = [i for i in sections if '@KML_' in i]
        self.csv_keys = [i for i in sections if '@CSV_' in i]
        
        self.general = {'origin_distance':0,\
                        'offset_variable':None,\
                        'unit_length':1,\
                        'owntrack':None,\
                        'output_path':'./result',\
                        'backimg':None}
        if '@TSUTSUJI_GENERAL' in sections:
            for k in self.cp.options('@TSUTSUJI_GENERAL'):
                self.general[k] = self.cp['@TSUTSUJI_GENERAL'][k] if k not in ['origin_distance', 'unit_length'] else float(self.cp['@TSUTSUJI_GENERAL'][k])
            self.owntrack = self.general['owntrack']
            self.general['output_path'] = self.path_parent.joinpath(pathlib.Path(self.general['output_path']))
            if self.general['backimg'] is not None:
                self.general['backimg'] = self.path_parent.joinpath(pathlib.Path(self.general['backimg']))
                
        self.track_data = self.get_trackdata(self.track_keys)
        for tk in self.track_keys:
            if self.track_data[tk]['isowntrack']:
                self.owntrack = tk

        self.kml_track = self.get_trackdata(self.kml_keys)
        self.csv_track = self.get_trackdata(self.csv_keys)

        self.maptile = None
                        
        if '@MAPTILE' in sections:
            self.maptile = {'toshow': False,\
                        'longitude': 139.741357472222222,\
                        'latitude':  35.6580992222222222,\
                        'x0': 0,\
                        'y0': 0,\
                        'alpha': 0.8,\
                        'zoomlevel': 15,\
                        'template_url': '',\
                        'autozoom': False}
            for key in self.cp.options('@MAPTILE'):
                self.maptile[key] = self.cp['@MAPTILE'][key]
            for key in ['longitude', 'latitude', 'x0', 'y0', 'alpha']:
                if key in self.cp.options('@MAPTILE'):
                    self.maptile[key] = float(self.maptile[key])
            key = 'zoomlevel'
            if key in self.cp.options('@MAPTILE'):
                self.maptile[key] = int(self.maptile[key])
            for key in ['toshow', 'autozoom']:
                if key in self.cp.options('@MAPTILE'):
                    self.maptile[key] = True if self.maptile[key]=='True' else False
            
    def get_trackdata(self, keys):
        track_data = {}
        linecolor_default = ['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd','#8c564b','#e377c2','#7f7f7f','#bcbd22','#17becf']
        color_ix = 0

        for tk in keys:
            track_data[tk] = {'absolute_coordinate':True,\
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
                                    'color':linecolor_default[color_ix%10],\
                                    'calc_relrad':False}
            for k in self.cp.options(tk):
                if k.lower() == 'file':
                    track_data[tk][k] = self.path_parent.joinpath(pathlib.Path(self.cp[tk][k]))
                elif k.lower() in ['x','y','z','angle','endpoint','origin_kilopost']:
                    track_data[tk][k] = float(self.cp[tk][k])
                elif k.lower() in ['isowntrack','absolute_coordinate','calc_relrad']:
                    track_data[tk][k] = True if self.cp[tk][k].lower() == 'true' else False
                elif k.lower() in ['supplemental_cp']:
                    for supcp in self.cp[tk][k].split(','):
                        track_data[tk][k].append(float(supcp))
                else:
                    track_data[tk][k] = self.cp[tk][k]
            color_ix +=1
        return track_data
        

