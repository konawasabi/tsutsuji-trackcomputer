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

def readfile(filename,offset_label, result_list, input_root, include_file=None):
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
                    readfile(input_root.joinpath(re.sub('\'','',tree.children[0].children[0])),\
                               offset_label,\
                               result_list,\
                               input_root = input_root,\
                               include_file = re.sub('\'','',tree.children[0].children[0]))
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
            
    result_list.append({'filename':filename, 'include_file':include_file, 'data':output})

def writefile(result, output_root):
    for data in result:
        include_file = data['include_file']
        filename = data['filename']
        output = data['data']
        if include_file is None:
            os.makedirs(output_root,exist_ok=True)
            fp = open(output_root.joinpath(pathlib.Path(filename).name),'w')
        else:
            os.makedirs(output_root.joinpath(pathlib.Path(include_file).parent),exist_ok=True)
            fp = open(output_root.joinpath(include_file),'w')
        fp.write(output)
        fp.close()

        print(filename)
        print(output)

if __name__ == '__main__':
    input_path = pathlib.Path(sys.argv[1])
    inroot = input_path.parent
    outroot = inroot.joinpath('result')
    #input_path = sys.argv[1]
    result = []
    readfile(str(input_path), '$hoge', result, inroot)
    writefile(result, outroot)
