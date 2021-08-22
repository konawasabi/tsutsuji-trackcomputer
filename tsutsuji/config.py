import configparser
import pathlib

class Config():
    def __init__(self,path):
        cp = configparser.ConfigParser()
        cp.read(path)
        self.path_parent = pathlib.Path(path).resolve().parent
        sections = cp.sections()
        track_keys = [i for i in sections if i != '@GENERAL']
        
        self.general = {'origin_distance':0, 'offset_variable':'offset'}
        if '@GENERAL' in sections:
            for k in cp.options('@GENERAL'):
                self.general[k] = cp['@GENERAL'][k] if k not in ['origin_distance'] else float(cp['@GENERAL'][k])
            
        self.track_data = {}
        for tk in track_keys:
            self.track_data[tk] = {'origin':'absolute','x':0,'y':0,'z':0,'angle':0,'endpoint':0}
            for k in cp.options(tk):
                self.track_data[tk][k] = cp[tk][k] if k not in ['x','y','z','angle','endpoint'] else float(cp[tk][k])
