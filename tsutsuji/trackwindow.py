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

import tkinter as tk
from tkinter import ttk
import tkinter.simpledialog as simpledialog
import tkinter.colorchooser as colorchooser
from ttkwidgets import CheckboxTreeview

class TrackWindow(ttk.Frame):
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        #self.parent = master
    def create_window(self):
        #super().__init__(self.parent, padding='3 3 3 3')
        self.master = tk.Toplevel(self.mainwindow)
        
        self.mainwindow.tk.eval("""
            ttk::style map Treeview \
            -foreground {disabled SystemGrayText \
                         selected SystemHighlightText} \
            -background {disabled SystemButtonFace \
                         selected SystemHighlight}
        """)

        self.master.title('Tracks')
        #self.master.columnconfigure(0, weight=1)
        #self.master.rowconfigure(0, weight=1)
        #self.grid(column=0, row=0,sticky=(tk.N, tk.W, tk.E, tk.S))

        self.mainframe = ttk.Frame(self.master, padding='3 3 3 3')
        self.mainframe.columnconfigure(0,weight=1)
        self.mainframe.rowconfigure(0,weight=1)
        self.mainframe.grid(column=0, row=0,sticky=(tk.N, tk.W, tk.E, tk.S))
        self.master.geometry('+1100+0')
        self.track_tree = CheckboxTreeview(self.mainframe, show='tree headings', columns=['linecolor'],selectmode='browse')
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
    def click_tracklist(self, event=None):
        '''軌道リストをクリックしたときのイベント処理
        '''
        if event != None:
            clicked_column = self.track_tree.identify_column(event.x)
            clicked_track = self.track_tree.identify_row(event.y)
            clicked_zone = getattr(event, 'widget').identify("element", event.x, event.y)
            if clicked_zone == 'image': #チェックボックスをクリックしたか
                #ischecked = self.track_tree.get_checked()
                #print(ischecked)
                for tkey in self.mainwindow.trackcontrol.track.keys():
                    self.mainwindow.trackcontrol.track[tkey]['toshow'] = False
                for tkey in self.track_tree.get_checked():
                    self.mainwindow.trackcontrol.track[tkey]['toshow'] = True
            elif clicked_zone == 'text':
                if clicked_column == '#1': #ラインカラーをクリックしたか
                    nowcolor = self.mainwindow.trackcontrol.conf.track_data[clicked_track]['color']
                    inputdata = colorchooser.askcolor(color=nowcolor)
                    if inputdata[1] != None:
                        self.mainwindow.trackcontrol.conf.track_data[clicked_track]['color'] = inputdata[1]
                        self.track_tree.tag_configure(clicked_track,foreground=inputdata[1])
                
    def set_treevalue(self):
        if self.track_tree.exists('root'):
            self.track_tree.delete('root')
        self.track_tree.insert("", "end", 'root', text='root', open=True)
        colorix = 0
        for i in self.mainwindow.trackcontrol.track.keys():
            self.track_tree.insert("root", "end", i, text=i,\
                                   values=('■■■'),\
                                   tags=(i,))
            self.track_tree.tag_configure(i,foreground=self.mainwindow.trackcontrol.conf.track_data[i]['color'])
            self.track_tree.change_state(i, 'checked' if self.mainwindow.trackcontrol.track[i]['toshow'] else 'unchecked')
    def reset_treevalue(self):
        if self.master.winfo_exists():
            self.set_treevalue()
