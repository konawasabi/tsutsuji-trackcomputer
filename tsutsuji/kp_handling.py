#
#    Copyright 2024 konawasabi
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
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as filedialog

from lark import Lark, Transformer, v_args, Visitor

from kobushi import loadmapgrammer as lgr
from kobushi import loadheader as lhe
from kobushi import mapinterpreter

class GUI():
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self.master = tk.Toplevel(self.mainwindow)
        self.master.title('Handling kiloposts')
        self.master.protocol('WM_DELETE_WINDOW', self.closewindow)

        self.create_widgets()
        self.sendtopmost()

        self.kphandling = KilopostHandling()
    def create_widgets(self):
        self.mainframe = ttk.Frame(self.master, padding='3 3 3 3')
        self.mainframe.columnconfigure(0,weight=1)
        self.mainframe.rowconfigure(0,weight=1)
        self.mainframe.grid(column=0, row=0,sticky=(tk.N, tk.W, tk.E, tk.S))

        # ---

        self.fileframe = ttk.Frame(self.mainframe, padding='3 3 3 3')
        self.fileframe.grid(column=0, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))

        self.input_v = tk.StringVar()
        self.output_v = tk.StringVar()

        self.input_b = ttk.Button(self.fileframe, text='Input', command=self.setinputpath)
        self.output_b = ttk.Button(self.fileframe, text='Output', command=self.setoutputpath)
        self.input_e = ttk.Entry(self.fileframe, textvariable=self.input_v,width=80)
        self.output_e = ttk.Entry(self.fileframe, textvariable=self.output_v,width=80)

        self.input_b.grid(column=0, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.input_e.grid(column=1, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.output_b.grid(column=0, row=1, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.output_e.grid(column=1, row=1, sticky = (tk.N, tk.W, tk.E, tk.S))

        # ---

        self.modeframe = ttk.Labelframe(self.mainframe, padding='3 3 3 3', text='Mode')
        self.modeframe.grid(column=0, row=1, sticky = (tk.N, tk.W, tk.S))

        self.modeframe_main = ttk.Frame(self.modeframe, padding='3 3 3 3')
        self.modeframe_main.grid(column=0, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))

        self.mode_v = tk.StringVar(value='3')

        self.mode3_rb = ttk.Radiobutton(self.modeframe_main, text='0. echo', value='3', variable=self.mode_v)
        self.mode0_rb = ttk.Radiobutton(self.modeframe_main, text='1. evaluate', value='0', variable=self.mode_v)
        self.mode1_rb = ttk.Radiobutton(self.modeframe_main, text='2. new variable', value='1', variable=self.mode_v)
        self.mode2_rb = ttk.Radiobutton(self.modeframe_main, text='3. conversion by new expression', value='2', variable=self.mode_v)

        self.mode3_rb.grid(column=0, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.mode0_rb.grid(column=1, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.mode1_rb.grid(column=2, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.mode2_rb.grid(column=3, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))

        self.output_origkp_v = tk.BooleanVar(value=False)
        self.output_origkp_chk = ttk.Checkbutton(self.modeframe, text='Output original kilopost', variable=self.output_origkp_v)

        self.sortbykp_v = tk.BooleanVar(value=False)
        self.sortbykp_chk = ttk.Checkbutton(self.modeframe, text='Sort by kilopost', variable=self.sortbykp_v)

        self.output_origkp_chk.grid(column=0, row=1, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.sortbykp_chk.grid(column=0, row=2, sticky = (tk.N, tk.W, tk.E, tk.S))
        # ---

        self.paramframe = ttk.Frame(self.mainframe, padding='3 3 3 3')
        self.paramframe.grid(column=0, row=2, sticky = (tk.N, tk.W,  tk.S))

        self.decval_v = tk.StringVar()
        self.decval_l = ttk.Label(self.paramframe, text='Initialization')
        self.decval_e = ttk.Entry(self.paramframe, textvariable=self.decval_v,width=80)

        self.newexpr_v = tk.StringVar()
        self.newexpr_l = ttk.Label(self.paramframe, text='New variable/expression')
        self.newexpr_e = ttk.Entry(self.paramframe, textvariable=self.newexpr_v,width=80)
        self.decval_l.grid(column=0, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.decval_e.grid(column=0, row=1, sticky = (tk.N, tk.W, tk.E, tk.S))
        
        self.newexpr_l.grid(column=0, row=2, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.newexpr_e.grid(column=0, row=3, sticky = (tk.N, tk.W, tk.E, tk.S))

        self.kprangeframe = ttk.Labelframe(self.paramframe, padding='3 3 3 3', text='Kilopost range')
        self.kprangeframe.grid(column=0, row=4, sticky = (tk.N, tk.W,  tk.S))

        self.startkp_v = tk.DoubleVar()
        self.startkp_en_v = tk.BooleanVar(value=False)
        self.startkp_b = ttk.Checkbutton(self.kprangeframe, text='start', variable=self.startkp_en_v, onvalue=True, offvalue=False)
        self.startkp_e = ttk.Entry(self.kprangeframe, textvariable=self.startkp_v,width=10)

        self.endkp_v = tk.DoubleVar()
        self.endkp_en_v = tk.BooleanVar(value=False)
        self.endkp_b = ttk.Checkbutton(self.kprangeframe, text='end', variable=self.endkp_en_v, onvalue=True, offvalue=False)
        self.endkp_e = ttk.Entry(self.kprangeframe, textvariable=self.endkp_v,width=10)

        self.startkp_b.grid(column=0, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.startkp_e.grid(column=1, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))
        
        self.endkp_b.grid(column=2, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))
        self.endkp_e.grid(column=3, row=0, sticky = (tk.N, tk.W, tk.E, tk.S))

        # ---

        self.buttonframe = ttk.Frame(self.mainframe, padding='3 3 3 3')
        self.buttonframe.grid(column=0, row=3, sticky = (tk.N, tk.W,  tk.S))

        self.doit_b = ttk.Button(self.buttonframe, text='Do It', command=self.doit)
        self.doit_b.grid(column=0, row=1, sticky = (tk.N, tk.W, tk.E, tk.S))
    def closewindow(self):
        self.master.withdraw()
    def sendtopmost(self, event=None):
        self.master.lift()
        self.master.focus_force()
    def setinputpath(self):
        path = filedialog.askopenfilename(initialdir=self.input_v.get())
        if path != '':
            self.input_v.set(path)
            pathobj = pathlib.Path(path)
            
            self.output_v.set(str(pathobj.parent.joinpath('result/')))
    def setoutputpath(self):
        path = filedialog.askdirectory(initialdir=self.output_v.get())
        if path != '':
            self.output_v.set(path)
    def doit(self):
        filename, input_root = self.kphandling.procpath(self.input_v.get())
        if self.startkp_en_v.get():
            startkp = self.startkp_v.get()
        else:
            startkp = None
        if self.endkp_en_v.get():
            endkp = self.endkp_v.get()
        else:
            endkp = None
        
        result = self.kphandling.readfile(filename,\
                                          input_root,\
                                          mode=self.mode_v.get(),\
                                          initialize=self.decval_v.get(),\
                                          newExpression=self.newexpr_v.get(),\
                                          kprange=(startkp,endkp),\
                                          output_origkp=self.output_origkp_v.get())

        self.kphandling.writefile(result, pathlib.Path(self.output_v.get()))


@v_args(inline=True)
class MapInterpreter(mapinterpreter.ParseMap):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def map_element(self, *argument):
        pass
    def include_file(self, path):
        pass
        
class KilopostHandling():
    def __init__(self):
        self.grammer = lgr.loadmapgrammer()
        self.parser = Lark(self.grammer, parser='lalr')
        self.initialize_interpreter()
    def initialize_interpreter(self):
        self.mapinterp = MapInterpreter(None,None,prompt=True)
    
    def readfile(self,filename, input_root, mode='0', initialize=None, newExpression=None, include_file=None,kprange=(None,None),output_origkp=False):
        '''マップファイルを読み込み、距離程を書き換える

        Parameters:
        -----
        filename : str
          読み込むファイルへのパス
        input_root : pathlib.Path
          読み込むファイルの親ディレクトリへのパス
        mode : str
          動作モード
          '0': 変数、式で記述された距離程を数値に置き換える
          '1': newExpressionで指定した形式で距離程を書き換える
        initialize : str
          ファイル冒頭に追加するマップ要素（newExpressionで使用する変数の初期化を想定）
        newExpression : str
          mode='1'で使用。距離程を書き換える数式。
        include_file : str
          マップファイル内include要素の引数を指定する
        kprange : (float, float)
          処理を行う距離程範囲を指定する。（距離程は変換前の値）
        output_origkp : bool
          距離程を書き換えるモード(3以外)で、書き換え前の値を出力する場合はTrue
        -----

        result_listのフォーマット
          [{'filename':str, 'data':str}, ...]

        '''

        if include_file is None:
            self.initialize_interpreter()
        result_list = []
        result_dict = {}

        path, rootpath, header_enc = lhe.loadheader(filename, 'BveTs Map ',2)
        fp = open(path,'r',encoding=header_enc)
        fp.readline()
        fbuff = fp.read()
        fp.close()

        output = 'BveTs Map 2.02\n'

        rem_comm = re.split('#.*\n',fbuff)
        comm = re.findall('#.*\n',fbuff)

        # ルートマップファイル(includeで読み込まれたマップでない)で、mode: new var. or conversion by new expr.の場合は、先頭にInitialization文字列を追加する。
        if include_file is None and (mode == '1' or mode == '2'):
            # mode: conversion by new expr.の場合は、Initialization文字列をパーサで解釈する
            if mode == '2':
                for elem in initialize.split(';'):
                    elem = re.sub('^\s*','',elem)
                    result = self.mapinterp.transform(self.mapinterp.parser.parse(elem+';'))
            output += '\n# added by kilopost handling\n{:s}\n'.format(initialize)

        ix_comm = 0
        evaluated_kp = 0.0
        for item in rem_comm:
            statements = item.split(';')
            for elem in statements:
                pre_elem = re.match('^\s*',elem).group(0)                
                elem = re.sub('^\s*','',elem)
                result = self.mapinterp.transform(self.mapinterp.parser.parse(elem+';'))
                newstatement = ''
                if len(elem)>0:
                    tree = self.parser.parse(elem+';')
                    if ((kprange[0] is not None and kprange[0] <= self.mapinterp.environment.predef_vars['distance']) or kprange[0] is None) and \
                       ((kprange[1] is not None and kprange[1] >= self.mapinterp.environment.predef_vars['distance']) or kprange[1] is None):
                        
                        if tree.data == 'set_distance':
                            evaluated_kp = self.mapinterp.environment.predef_vars['distance']
                            if mode == '0':
                                newstatement = pre_elem + '{:f};'.format(evaluated_kp)
                                if output_origkp:
                                    newstatement += '# {:s}'.format(elem)
                            elif mode == '1':
                                newstatement = pre_elem + '{:s};'.format(newExpression.replace('distance','{:f}'.format(evaluated_kp)))
                                if output_origkp:
                                    newstatement += '# {:s}'.format(elem)
                            elif mode == '2':
                                offset_expr_tree = self.mapinterp.parser.parse('{:s};'.format(newExpression))
                                new_kp = self.mapinterp.transform(offset_expr_tree.children[0])
                                newstatement = pre_elem + '{:f};'.format(new_kp)
                                if output_origkp:
                                    newstatement += '# {:s}'.format(elem)
                            elif mode == '3':
                                newstatement = pre_elem + elem + ';'
                        elif tree.data == 'include_file':
                            result_list += self.readfile(input_root.joinpath(re.sub('\'','',tree.children[0].children[0])),\
                                                         input_root,
                                                         mode=mode, \
                                                         initialize=initialize,\
                                                         newExpression=newExpression,\
                                                         include_file=re.sub('\'','',tree.children[0].children[0]),\
                                                         kprange=kprange)
                            newstatement = pre_elem + elem + ';'
                        else:
                            newstatement = pre_elem + elem + ';'
                    elif tree.data == 'set_variable':
                        newstatement = pre_elem + elem + ';'
                else:
                    newstatement = pre_elem

                output += newstatement

            if ix_comm < len(comm):
                output += comm[ix_comm]
                ix_comm+=1

        result_list.append({'filename':filename, 'include_file':include_file, 'data':output, 'data_dict':result_dict})
        return result_list
    def writefile(self,result, output_root):
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
    def procpath(self,pathstr):
        ''' readfileへ渡すPathオブジェクトを生成する
        '''
        input_path = pathlib.Path(pathstr)
        inroot = input_path.parent
        return input_path, inroot
