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
import sys
import pathlib
import re

from lark import Lark, Transformer, v_args

from kobushi import loadmapgrammer as lgr
from kobushi import loadheader as lhe

def singlefile(filename,offset_label):
    path, rootpath, header_enc = lhe.loadheader(filename, 'BveTs Map ',2)
    fp = open(path,'r',encoding=header_enc)
    fp.readline()
    fbuff = fp.read()
    fp.close()
    #print(fbuff)

    output = 'BveTs Map 2.02\n'

    grammer = lgr.loadmapgrammer()
    parser = Lark(grammer, parser='lalr')

    rem_comm = re.split('#.*\n',fbuff)
    comm = re.findall('#.*\n',fbuff)

    ix_comm = 0
    for item in rem_comm:
        statements = item.split(';')
        for elem in statements:
            pre_elem = re.match('^\s*',elem).group(0)                
            elem = re.sub('^\s*','',elem)
            if len(elem)>0:
                tree = parser.parse(elem+';')
                if tree.data == 'include_file':
                    singlefile(lhe.joinpath(rootpath,\
                                            re.sub('\'','',tree.children[0].children[0])),\
                               offset_label)
                    output += pre_elem + elem + ';'
                elif tree.data == 'set_distance':
                    output += pre_elem + offset_label + '+' + elem + ';'
                else:
                    output += pre_elem + elem + ';'
            else:
                output += pre_elem
        
        if ix_comm < len(comm):
            output += comm[ix_comm]
            ix_comm+=1

    os.makedirs(lhe.joinpath(rootpath,'results'),exist_ok=True)
    filename_stem = pathlib.PurePath(filename).stem
    filename_suffix = pathlib.PurePath(filename).suffix
    fp = open(lhe.joinpath(lhe.joinpath(rootpath,'results'),str(filename_stem)+'_conv'+str(filename_suffix)),'w')
    fp.write(output)
    fp.close()

    print(filename)
    print(output)

def process(filename):
    pass
    

if __name__ == '__main__':
    singlefile(sys.argv[1],'$hoge')
