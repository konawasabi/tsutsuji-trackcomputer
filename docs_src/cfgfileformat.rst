================
CFG file format
================

*******************
[@TSUTSUJI_GENERAL]
*******************

owntrack
=========
* type: string
* 自軌道として扱うtrackkey
    
unit_length
============  
* type: float
* 各軌道について軌道座標を計算する間隔 [m]

  * デフォルトでは1m

offset_variable
================  
* type: string
* 計算結果の距離程を :code:`$hoge + dist` の形で表すときの変数名。

   * このときdistの原点はorigin_distance。
   * 省略した場合は絶対距離程で表す。

origin_distance
================  
* type: float
* 計算結果の距離程始端

output_path
============
* type: filepath
* 変換結果を保存するディレクトリへのパス

  * cfgファイルが置かれた場所からの相対パスで記述する
  * 省略した場合は :code:`./result`

************
[*trackkey*]
************

* *trackkey* : 読み込む軌道名

file
===========
* type: filepath
* *trackkey* として読み込むmapファイルパス
* **省略不可**

absolute_coordinate
===================
* type: bool
* 軌道始点座標の指定方法
  
  * True: 絶対座標系
  * False: 別軌道のある距離程を基準とした座標系

    * ver1.0.0ではTrueのみ対応

parent_track
============
* type: string
* 座標系の原点となる軌道のtrackkey
* **absolute_coordinate == Falseの場合にのみ有効**
* ver1.0.0では未実装

origin_kilopost
===============
* type: float
* 座標系の原点となる距離程
* **absolute_coordinate == Falseの場合にのみ有効**
* ver1.0.0では未実装
 
x
==========
* type: float
* 軌道始端座標のx成分 [m]

y
===========
* type: float
* 軌道始端座標のy成分 [m]

z
===========
* type: float
* 軌道始端座標のz成分 [m]

angle
===========
* type: float
* 軌道始端における進行方角 [°]
* z軸方向を0とする。
  
* x, y, z, angle については下図を参照

.. image:: ./files/coordinate.png


isowntrack
===========
* type: bool
* この軌道を自軌道とする場合にTrue

  * [@TSUTSUJI_GENERAL]のowntrackを設定した場合は記述不要
  * 両方を記述した場合は最後に記述したものが反映される

endpoint
===========
* type: float
* 軌道終点の距離程 [m]

supplemental_cp
================
* type: float, float, ..., float
* 制御点として追加する距離程

color
======
* type: string
* 軌道プロット時の線色

  * 16進数カラーコード('#rrggbb')または色名で指定
  * デフォルトでは読み込んだ軌道ごとに下記の順序で設定
    
    * '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
      
  * 指定できる色名(https://matplotlib.org/2.0.2/examples/color/named_colors.html をもとに作成)
.. image:: ./files/namedcolor.png
