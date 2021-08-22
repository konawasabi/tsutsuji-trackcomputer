import configparser
import pathlib

class Config():
    def __init__(self,path):
        cp = configparser.ConfigParser()
        cp.read(path)
        self.path_parent = pathlib.Path(path).resolve().parent
        sections = cp.sections()
        self.track_keys = [i for i in sections if i != '@GENERAL']
        
        self.general = {'origin_distance':0, 'offset_variable':'offset', 'resolution':1}
        if '@GENERAL' in sections:
            for k in cp.options('@GENERAL'):
                self.general[k] = cp['@GENERAL'][k] if k not in ['origin_distance', 'resolution'] else float(cp['@GENERAL'][k])
            
        self.track_data = {}
        for tk in self.track_keys:
            self.track_data[tk] = {'absolute_coordinate':True,\
                                    'x':0,\
                                    'y':0,\
                                    'z':0,\
                                    'angle':0,\
                                    'endpoint':0,\
                                    'file':None,\
                                    'parent_track':None,\
                                    'origin_distance':None,\
                                    'isowntrack':False}
            for k in cp.options(tk):
                if k.lower() == 'file':
                    self.track_data[tk][k] = self.path_parent.joinpath(pathlib.Path(cp[tk][k]))
                elif k.lower() in ['x','y','z','angle','endpoint','origin_distance']:
                    self.track_data[tk][k] = float(cp[tk][k])
                elif k.lower() in ['isowntrack','absolute_coordinate']:
                    self.track_data[tk][k] = True if cp[tk][k].lower() == 'true' else False
                else:
                    self.track_data[tk][k] = cp[tk][k]
                    
