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
import argparse

from lark import Lark, Transformer, v_args, Visitor

from kobushi import loadmapgrammer as lgr
from kobushi import loadheader as lhe

def readfile(filename, offset_label, offset_val, result_list, input_root, include_file=None, inverse_kp = False):
    '''マップファイルを読み込み、距離程に指定のラベルを加算した文字列を生成する
    
    Parameters:
    -----
    filename : str
      読み込むファイルへのパス
    offset_label : str
      距離程の先頭へ追加する文字列
    offset_val : float or None
      offset_labelへ代入する値。Noneなら代入構文を出力しない。
    result_list : list
      結果を格納するリスト。
    input_root : pathlib.Path
      読み込むファイルの親ディレクトリへのパス
    include_file : str
      マップファイル内include要素の引数を指定する
    inverse_kp : bool
      Trueの場合、読み込んだ距離程を-1倍して出力する
    -----

    result_listのフォーマット
      [{'filename':str, 'data':str}, ...]
    
    '''
    if False:
        import pdb
        pdb.set_trace()

    class detectDistance(Visitor):
        def __init__(self, *args, **kwargs):
            super().__init__()
            self.isdistance = args[0]
        def call_predefined_variable(self, tree):
            if tree.children[0].value == 'distance':
                self.isdistance[0] = True
    
    path, rootpath, header_enc = lhe.loadheader(filename, 'BveTs Map ',2)
    fp = open(path,'r',encoding=header_enc)
    fp.readline()
    fbuff = fp.read()
    fp.close()

    output = 'BveTs Map 2.02\n'

    if offset_val is not None:
        output += '\n{:s} = {:f};\n'.format(offset_label, offset_val)

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
                               offset_val,\
                               result_list,\
                               input_root = input_root,\
                               include_file = re.sub('\'','',tree.children[0].children[0]))
                    output += pre_elem + elem + ';'
                elif tree.data == 'set_distance':
                    isdistance = [False]
                    detectDistance(isdistance).visit(tree)
                    if not isdistance[0]:
                        if inverse_kp:
                            output += pre_elem + offset_label + ' - ({:s})'.format(elem) + ';'
                        else:
                            output += pre_elem + offset_label + ' + ' +  elem + ';'
                    else:
                        if inverse_kp:
                            output += pre_elem + ' - ({:s})'.format(elem) + ';'
                        else:
                            output += pre_elem +  elem + ';'
                else:
                    output += pre_elem + elem + ';'
            else:
                output += pre_elem
        
        if ix_comm < len(comm):
            output += comm[ix_comm]
            ix_comm+=1
            
    result_list.append({'filename':filename, 'include_file':include_file, 'data':output})

def writefile(result, output_root):
    ''' readfileで生成したresult_listをファイルに出力する

    Parameters:
    -----
    result : list
      readfileが出力するresult_list
    output_root : pathlib.Path
      データを出力するディレクトリへのパス
    '''
    for data in result:
        if data['include_file'] is None:
            os.makedirs(output_root,exist_ok=True)
            fp = open(output_root.joinpath(pathlib.Path(data['filename']).name),'w')
        else:
            os.makedirs(output_root.joinpath(pathlib.Path(data['include_file']).parent),exist_ok=True)
            fp = open(output_root.joinpath(data['include_file']),'w')
        fp.write(data['data'])
        fp.close()

        if False:
            print(data['filename'])
            print(data['data'])

def procpath(pathstr):
    ''' readfileへ渡すPathオブジェクトを生成する
    '''
    input_path = pathlib.Path(pathstr)
    inroot = input_path.parent
    return input_path, inroot

if __name__ == '__main__':
    argp = argparse.ArgumentParser()
    argp.add_argument('filepath', metavar='FILE', type=str, help='input map file', nargs='?')
    argp.add_argument('-l', '--label', help='offest label (default: hoge)', type=str, default='hoge')
    argp.add_argument('-d', '--distance', help='offset distance (default: 0.0)', type=float, default=0.0)
    argp.add_argument('-i', '--invert', help='invert the values of kiloposts', action='store_true')
    argp.add_argument('-o', '--outputdir', help='output directory', type=str)
    args = argp.parse_args()
    
    input_path, inroot = procpath(args.filepath)
    if args.outputdir is None:
        outroot = inroot.joinpath('result')
    else:
        outroot = pathlib.Path(args.outputdir)

    result = []
    readfile(str(input_path), '$'+args.label, args.distance,  result, inroot, inverse_kp = args.invert)
    writefile(result, outroot)
