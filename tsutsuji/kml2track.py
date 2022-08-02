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

import os
import pathlib
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate
import xml.etree.ElementTree as ET

from kobushi import mapinterpreter
from kobushi import trackgenerator

from . import config
from . import math

class Kml2track():
    def __init__(self):
        self.initialize_variables()
    def initialize_variables(self):
        self.track = {}
    def loadkml(self, path):
        data = []
        tree = ET.parse(path)
        root = tree.getroot()
        for line in root.iter('*'):
            if line.tag == '{http://www.opengis.net/kml/2.2}coordinates':
                for i in line.text.strip().split(' '):
                    tmp = i.split(',')
                    if len(tmp)==3:
                        data.append([float(tmp[0]),float(tmp[1]),float(tmp[2])])
                    else:
                        data.append([float(tmp[0]),float(tmp[1]),float(0)])

        output = []
        for i in range(1,len(data)):
            tmp = math.calc_pl2xy(data[i][1],data[i][0],data[0][1],data[0][0])
            output.append([tmp[0],tmp[1],data[i][2]])

        output = np.array(output)
        return output
    def loadcsv(self, path):
        data = np.loadtxt(path, delimiter=',')
        return data
    def load_files(self, conf):
        for key in conf.kml_keys:
            self.track[key] = {}
            self.track[key]['data'] = self.loadkml(conf.kml_track[key]['file'])
            self.track[key]['color'] = conf.kml_track[key]['color']
            self.track[key]['conf'] = conf.kml_track[key]
        for key in conf.csv_keys:
            self.track[key] = {}
            self.track[key]['data'] = self.loadcsv(conf.csv_track[key]['file'])
            self.track[key]['color'] = conf.csv_track[key]['color']
            self.track[key]['conf'] = conf.csv_track[key]
        for key in self.track.keys():
            self.track[key]['interp'] = None
            self.track[key]['tgen'] = None
            self.track[key]['cplist_symbol'] = None
            self.track[key]['output_mapfile'] = None
            
            self.track[key]['toshow'] = True
            self.track[key]['result'] = self.generate_trackdata(self.track[key]['data'], self.track[key]['conf'])
    def generate_trackdata(self, data, conf):
        distance = 0
        theta = 0
        result = []
        data_rot = [[conf['x'],conf['y'],conf['z']]]
        for ix in range(0,len(data)):
            elem_rot = np.dot(math.rotate(np.deg2rad(conf['angle'])),\
                              np.array([data[ix][0],data[ix][1]]))
            data_rot.append([elem_rot[0]+conf['x'],elem_rot[1]+conf['y'],data[ix][2]+conf['z']])
        for ix in range(0,len(data)):
            #[[distance,xpos,ypos,zpos,theta,radius,gradient,interpolate_func,cant,center,gauge],[d.,x.,y.,...],[...],...]
            if ix < len(data_rot)-1:
                theta = np.arctan((data_rot[ix+1][1]-data_rot[ix][1])/((data_rot[ix+1][0]-data_rot[ix][0])))
            if ix > 0:
                distance += np.sqrt((data_rot[ix][0]-data_rot[ix-1][0])**2+(data_rot[ix][1]-data_rot[ix-1][1])**2)
            result.append([distance,\
                           data_rot[ix][0],\
                           data_rot[ix][1],\
                           data_rot[ix][2],\
                           theta,\
                           0,\
                           0,\
                           0,\
                           0,\
                           0,\
                           0])
        result_np = np.array(result)
        
        return result_np
    def plot2d(self, ax):
        for key in self.track.keys():
            if self.track[key]['toshow']:
                tmp = self.track[key]['result']
                ax.plot(tmp[:,1],tmp[:,2],label=key,color=self.track[key]['color'])
    def drawarea(self, extent_orig):
        extent = extent_orig
        for key in self.track.keys():
            tmp_src = self.track[key]['result']
            tmp_result = [min(tmp_src[:,1]),max(tmp_src[:,1]),min(tmp_src[:,2]),max(tmp_src[:,2])]
            extent[0] = tmp_result[0] if tmp_result[0] < extent[0] else extent[0]
            extent[1] = tmp_result[1] if tmp_result[1] > extent[1] else extent[1]
            extent[2] = tmp_result[2] if tmp_result[2] < extent[2] else extent[2]
            extent[3] = tmp_result[3] if tmp_result[3] > extent[3] else extent[3]
        return extent
        
