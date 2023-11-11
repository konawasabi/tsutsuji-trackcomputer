#
#    Copyright 2022 konawasabi
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

import re

import tkinter as tk
from tkinter import ttk
import tkinter.simpledialog as simpledialog
import tkinter.colorchooser as colorchooser
from ttkwidgets import CheckboxTreeview

class TrackWindow(ttk.Frame):
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        #self.parent = master
        self.master = None
    def create_window(self):
        #super().__init__(self.parent, padding='3 3 3 3')
        if self.master is None:
            self.master = tk.Toplevel(self.mainwindow)

            self.mainwindow.tk.eval("""
                ttk::style map Treeview \
                -foreground {disabled SystemGrayText \
                             selected SystemHighlightText} \
                -background {disabled SystemButtonFace \
                             selected SystemHighlight}
            """)

            self.master.title('Tracks')
            self.master.protocol('WM_DELETE_WINDOW', self.closewindow)

            self.mainframe = ttk.Frame(self.master, padding='3 3 3 3')
            self.mainframe.columnconfigure(0,weight=1)
            self.mainframe.rowconfigure(0,weight=1)
            self.mainframe.grid(column=0, row=0,sticky=(tk.N, tk.W, tk.E, tk.S))
            self.master.geometry('+1100+0')
            self.track_tree = CheckboxTreeview_tsutsuji(self.mainframe, show='tree headings', columns=['linecolor'],selectmode='browse')
            self.track_tree.bind("<ButtonRelease>", self.click_tracklist)
            self.track_tree.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
            self.track_tree.column('#0', width=200)
            self.track_tree.column('linecolor', width=50)
            self.track_tree.heading('#0', text='track key')
            self.track_tree.heading('linecolor', text='Color')

            self.tree_scrollbar = ttk.Scrollbar(self.mainframe, orient=tk.VERTICAL, command=self.track_tree.yview)
            self.tree_scrollbar.grid(column=1, row=0, sticky=(tk.N, tk.S, tk.E))
            self.track_tree.configure(yscrollcommand=self.tree_scrollbar.set)

            self.set_treevalue()
        else:
            self.sendtopmost()
    def click_tracklist(self, event=None):
        '''軌道リストをクリックしたときのイベント処理
        '''
        if event != None:
            clicked_column = self.track_tree.identify_column(event.x)
            clicked_track = self.track_tree.identify_row(event.y)
            clicked_track_rematt = re.sub('@GT_','',clicked_track)
            clicked_zone = getattr(event, 'widget').identify("element", event.x, event.y)
            focused = self.track_tree.focus()
            parent = self.track_tree.parent(focused)
            if clicked_zone == 'image': #チェックボックスをクリックしたか
                # rootをクリックした場合、cfgファイルから読み込んだ軌道を一括設定
                if clicked_track == 'root': 
                    for tkey in self.track_tree.get_children('root'):
                        target = self.mainwindow.trackcontrol.track[tkey]
                        if self.track_tree.tag_has("checked", 'root'):
                            target['toshow'] = True
                        else:
                            target['toshow'] = False
                        for otkey in self.track_tree.get_children(tkey):
                            ot_target = target['othertrack'][re.sub('@OT_','',otkey)]
                            if self.track_tree.tag_has("checked", 'root'):
                                ot_target['toshow'] = True
                            else:
                                ot_target['toshow'] = False
                # seq_points をクリックした場合、kml/csvファイルから読み込んだ点列を一括設定
                elif clicked_track == 'seq_points':
                    for tkey in self.track_tree.get_children(clicked_track):
                        target = self.mainwindow.trackcontrol.pointsequence_track.track[tkey]
                        if self.track_tree.tag_has("checked", clicked_track):
                            target['toshow'] = True
                        else:
                            target['toshow'] = False
                # generatedをクリックした場合、計算した他軌道を一括設定
                elif clicked_track == 'generated':
                    for tkey in self.track_tree.get_children(clicked_track):
                        target = self.mainwindow.trackcontrol.generated_othertrack[re.sub('@OT_','',tkey)]
                        if self.track_tree.tag_has("checked", clicked_track):
                            target['toshow'] = True
                        else:
                            target['toshow'] = False
                # 個別のtrack(自軌道形式)をクリックした場合
                elif parent == 'root':
                    target = self.mainwindow.trackcontrol.track[clicked_track]
                    if self.track_tree.tag_has("checked", clicked_track):
                        target['toshow'] = True
                    else:
                        target['toshow'] = False
                # 個別のKML/CSV点列をクリックした場合
                elif parent == 'seq_points':
                    target = self.mainwindow.trackcontrol.pointsequence_track.track[clicked_track]
                    if self.track_tree.tag_has("checked", clicked_track):
                        target['toshow'] = True
                    else:
                        target['toshow'] = False
                # 自軌道に従属する他軌道をクリックした場合
                elif '@OT_' in clicked_track: 
                    clicked_track_rm = re.sub('@OT_','',focused)
                    target = self.mainwindow.trackcontrol.track[self.track_tree.parent(focused)]['othertrack'][clicked_track_rm]
                    if self.track_tree.tag_has("checked", focused):
                        target['toshow'] = True
                    else:
                        target['toshow'] = False
                # 個別の他軌道をクリックした場合
                else:
                    target = self.mainwindow.trackcontrol.generated_othertrack[clicked_track_rematt]
                    if self.track_tree.tag_has("checked", focused):
                        target['toshow'] = True
                    else:
                        target['toshow'] = False
            elif clicked_zone == 'text':
                #ラインカラーをクリックしたら、カラーピッカーを開く
                if clicked_column == '#1': 
                    if '@' not in clicked_track:
                        nowcolor = self.mainwindow.trackcontrol.conf.track_data[clicked_track]['color']
                    elif '@OT_' in clicked_track:
                        clicked_track_rm = re.sub('@OT_','',focused)
                        nowcolor = self.mainwindow.trackcontrol.track[parent]['othertrack'][clicked_track_rm]['color']
                            
                    elif '@KML_' in clicked_track or '@CSV_' in clicked_track:
                        nowcolor = self.mainwindow.trackcontrol.pointsequence_track.track[clicked_track]['color']
                    else:
                        nowcolor = self.mainwindow.trackcontrol.generated_othertrack[clicked_track_rematt]['color']
                    inputdata = colorchooser.askcolor(color=nowcolor)
                    if inputdata[1] != None: # カラーピッカーでキャンセルされなかった場合、当該軌道に色を指定
                        if '@' not in clicked_track:
                            self.mainwindow.trackcontrol.conf.track_data[clicked_track]['color'] = inputdata[1]
                            self.track_tree.tag_configure(clicked_track,foreground=inputdata[1])
                        elif '@OT_' in clicked_track: 
                            clicked_track_rm = re.sub('@OT_','',focused)
                            self.mainwindow.trackcontrol.track[parent]['othertrack'][clicked_track_rm]['color'] = inputdata[1]
                            self.track_tree.tag_configure(clicked_track,foreground=inputdata[1])
                        elif '@KML_' in clicked_track or '@CSV_' in clicked_track:
                            self.mainwindow.trackcontrol.pointsequence_track.track[clicked_track]['color'] = inputdata[1]
                            self.track_tree.tag_configure(clicked_track,foreground=inputdata[1])
                        else:
                            self.mainwindow.trackcontrol.generated_othertrack[clicked_track_rematt]['color'] = inputdata[1]
                            self.track_tree.tag_configure(clicked_track,foreground=inputdata[1])
            self.mainwindow.drawall()
    def set_treevalue(self):
        ''' 軌道データをツリーリストに表示する
        '''
        # cfgファイルから読み込んだ軌道の表示
        if self.track_tree.exists('root'):
            self.track_tree.delete('root')
        self.track_tree.insert("", "end", 'root', text='root', open=True)
        colorix = 0
        for i in self.mainwindow.trackcontrol.track.keys():
            self.track_tree.insert("root", "end", i, text=i,\
                                   values=('■■■'),\
                                   tags=(i,),\
                                   open=True)
            self.track_tree.tag_configure(i,foreground=self.mainwindow.trackcontrol.conf.track_data[i]['color'])
            self.track_tree.change_state(i, 'checked' if self.mainwindow.trackcontrol.track[i]['toshow'] else 'unchecked')

            # 従属する他軌道の表示
            for otkey in self.mainwindow.trackcontrol.track[i]['othertrack'].keys():
                self.track_tree.insert(i,"end",'@OT_'+otkey,text=otkey,values=('■■■'),\
                                       tags=('@OT_'+otkey,))
                self.track_tree.tag_configure('@OT_'+otkey,foreground=self.mainwindow.trackcontrol.track[i]['othertrack'][otkey]['color'])
                self.track_tree.change_state('@OT_'+otkey, 'checked' if self.mainwindow.trackcontrol.track[i]['othertrack'][otkey]['toshow'] else 'unchecked')

        # KML/CSVから読み込んだ点列データの表示
        label_sqtr = 'seq_points'
        if self.track_tree.exists(label_sqtr):
            self.track_tree.delete(label_sqtr)
        self.track_tree.insert("", "end", label_sqtr, text=label_sqtr, open=True)
        for i in self.mainwindow.trackcontrol.pointsequence_track.track.keys():
            self.track_tree.insert(label_sqtr, "end", i, text=i,\
                                   values=('■■■'),\
                                   tags=(i,))
            self.track_tree.tag_configure(i,foreground=self.mainwindow.trackcontrol.pointsequence_track.track[i]['color'])
            self.track_tree.change_state(i, 'checked' if self.mainwindow.trackcontrol.pointsequence_track.track[i]['toshow'] else 'unchecked')

        # generateした他軌道の表示
        if self.track_tree.exists('generated'):
            self.track_tree.delete('generated')
        self.track_tree.insert("", "end", 'generated', text='generated', open=True)
        if self.mainwindow.trackcontrol.generated_othertrack is not None:
            for i in self.mainwindow.trackcontrol.generated_othertrack.keys():
                self.track_tree.insert("generated", "end", '@GT_'+i, text=i,\
                                       values=('■■■'),\
                                       tags=('@GT_'+i,))
                self.track_tree.tag_configure('@GT_'+i,foreground=self.mainwindow.trackcontrol.generated_othertrack[i]['color'])
                self.track_tree.change_state('@GT_'+i, 'checked' if self.mainwindow.trackcontrol.generated_othertrack[i]['toshow'] else 'unchecked')
    def reset_treevalue(self):
        ''' ツリーリストを再構築する
        '''

        # track windowが表示されている場合にのみ再構築
        if self.master is not None:
            self.set_treevalue()
    def closewindow(self):
        self.master.withdraw()
        self.master = None
    def sendtopmost(self,event=None):
        self.master.lift()
        self.master.focus_force()

class CheckboxTreeview_tsutsuji(CheckboxTreeview):
    ''' 子要素のチェックを全てon/offした場合に親要素のチェックを操作しないように変更
    '''
    def _check_ancestor(self, item):
        self.change_state(item, "checked")
    def _uncheck_ancestor(self, item):
        self.change_state(item, "unchecked")
