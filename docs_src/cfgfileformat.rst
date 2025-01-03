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

  * デフォルトでは1 [m]

* この数値によって軌道位置の計算精度が決まる
  
  * 極端に小さな値を設定すると、計算に必要なメモリ、時間が大幅に増えるので注意

offset_variable
================  
* type: string
* 変換結果の距離程を :code:`$offset_variable + distance;` の形で表すときの変数名。

  * 省略した場合はdistanceのみで表す。

origin_distance
================  
* type: float

  * offset_variableで指定した変数に代入する数値

output_path
============
* type: filepath
* 変換結果を保存するディレクトリへのパス

  * cfgファイルが置かれた場所からの相対パスで記述する
  * 省略した場合は :code:`./result`

backimg
========
* type: filepath
* 線形データ読み込み時に表示する背景画像設定ファイルへのパス

  * オプションメニュー -> Save Backimg... で出力したファイルを指定する

backimg_height
=================
* type: filepath
* 高度ウィンドウへ表示する背景画像設定ファイルへのパス

  * 高度メニュー -> Save Backimg... で出力したファイルを指定する

output_digit
==============
* type: int
* マップファイル出力時の各パラメータ小数点以下桁数

  * デフォルトでは 3

check_u
=========
* type: bool
* 自軌道法線に対して対象軌道が2回交差するかどうか（下図参照）を判別するルーチンを実行する場合はTrue

  * デフォルトでは True


.. image:: ./files/cfgformat_checkU.png

limit_curvatureradius
======================
* type: float
* 出力する相対半径の上限値を設定する

  * 計算結果の絶対値がこの値を超えた場合、相対半径は0として出力される
  * デフォルトでは 1e4  


************
[*trackkey*]
************

* *trackkey* : 読み込む軌道データに与える軌道キー

  * `@KML_` で始まる文字列を指定した場合、 `file` で指定したkmlファイルから座標データを読み込む
  * `@CSV_` で始まる文字列を指定した場合、 `file` で指定したcsvファイルから座標データを読み込む
  * mapファイルから軌道データを読み込む場合、軌道キーの先頭に `@` は使用できない

file
===========
* type: filepath
* *trackkey* として読み込むファイルパス
* 指定できるファイルのフォーマットについては :doc:`trackfileformat` を参照
* **省略不可**

absolute_coordinate
===================
* type: bool
* 軌道始点座標の指定方法
  
  * True: 絶対座標系
  * False: 別軌道のある距離程を基準とした座標系

    * `parent_track` で指定した軌道の距離程\ `origin_kilopost` の座標を原点として、\ `x` ,\ `y` ,\ `z`  で指定した距離オフセットした位置を軌道始点とする

* kml/csvファイルから読み込んだ軌道に対しては `True` のみ有効

parent_track
============
* type: string
* 座標系の原点となる軌道のtrackkey
* **absolute_coordinate == Falseの場合にのみ有効**

origin_kilopost
===============
* type: float
* 座標系の原点となる距離程
* **absolute_coordinate == Falseの場合にのみ有効**
 
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
* 軌道始端における進行方向 [°]
* `absolute_coordinate = True` の場合、絶対座標系のz軸方向を0とする
* `absolute_coordinate = False` の場合、相対座標系のz軸方向(指定された距離程での軌道の向き)を0とする
  
  
* x, y, z, angle については下図を参照

  * 下図のTrack A, B始端座標について

    * Track Aの(x, y, z, φ) = (0, y\ :sub:`0`\, z\ :sub:`0`\, 0)
    * Track Bの(x, y, z, φ) = (x\ :sub:`0`\, y\ :sub:`0`\, z\ :sub:`0`\, φ\ :sub:`0`\)
  

.. image:: ./files/coordinate.png


isowntrack
===========
* type: bool
* この軌道を自軌道とする場合にTrue

  * [@TSUTSUJI_GENERAL]のowntrackを設定した場合は記述不要
  * 両方を記述した場合は最後に記述したものが反映される
  * kml/csvファイルから読み込んだ軌道に対しては無効

endpoint
===========
* type: float
* 軌道終点の距離程 [m]

supplemental_cp
================
* type: float, float, ..., float
* 制御点として追加する距離程

  * コンマ区切りリストで記述する
  * 注目している軌道基準での該当する距離程でTrack構文を出力する

color
======
* type: string
* 軌道プロット時の線色

  * 16進数カラーコード('#rrggbb')または色名で指定
  * デフォルトでは読み込んだ軌道ごとに下記の順序で設定
    
    * .. image:: ./files/color_default.png
	   :scale: 50%
      
  * 指定できる色名

    * https://matplotlib.org/2.0.2/examples/color/named_colors.html をもとに作成
    * .. image:: ./files/namedcolor.png
	   :scale: 75%

calc_relrad
=============
* type: bool
* 相対半径を出力するかどうか設定する
* デフォルトではFalse
  
  * 出力されるTrack構文の相対半径は全て0となる
    
* **kml/csvファイルに対する軌道のみ有効**


mapelement_enable_x
=====================
* type: bool
* 他軌道構文として出力する際、 `Track[key].X` 要素を出力するかどうか設定する
* デフォルトではTrue

mapelement_enable_y
=====================
* type: bool
* 他軌道構文として出力する際、 `Track[key].Y` 要素を出力するかどうか設定する
* デフォルトではTrue

mapelement_enable_cant
=====================
* type: bool
* 他軌道構文として出力する際、 `Track[key].Cant.Interpolate` 要素を出力するかどうか設定する
* デフォルトではTrue

mapelement_enable_interpolate_func
=====================
* type: bool
* 他軌道構文として出力する際、 `Track[key].Cant.SetFunction` 要素を出力するかどうか設定する
* デフォルトではTrue
  
mapelement_enable_center
=====================
* type: bool
* 他軌道構文として出力する際、 `Track[key].Cant.SetCenter` 要素を出力するかどうか設定する
* デフォルトではTrue

mapelement_enable_gauge
=====================
* type: bool
* 他軌道構文として出力する際、 `Track[key].Cant.SetGauge` 要素を出力するかどうか設定する
* デフォルトではTrue


.. _ref_cfg_maptile:

************
[@MAPTILE]
************

longitude
===========
* type: float
* tsutsuji上の座標(x0, y0)に対応するマップタイルの経度 [deg]

  * 東経を正とする
  
* default: 139.741357472222222

latitude
===========
* type: float
* tsutsuji上の座標(x0, y0)に対応するマップタイルの緯度 [deg]

  * 北緯を正とする

* default: 35.6580992222222222

.. note::

  * 経度・緯度が度(°), 分(′), 秒(″)で表されている場合は度に変換すること
  * 変換式: a°b′c″ に対して a + (b + c/60)/60 [deg]
   

x0
======
* type: float
* マップタイル上の位置(longitude, latitude)に対応するtsutsuji上の座標x成分 [m]
* default: 0

y0
=====
* type: float
* マップタイル上の位置(longitude, latitude)に対応するtsutsuji上の座標y成分 [m]
* default: 0

alpha
=======
* type: float
* Tsutsuji起動時のマップ透過率 [0-1]
* default: 1.0

zoomlevel
=============
* type: float
* Tsutsuji起動時のズームレベル [0-18]
* default: 15

template_url
==============
* type: string
* XYZ形式で記述されたマップタイルのテンプレートURL

  * 国土地理院タイル
    
    * 標準地図なら `https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png`
    * 空中写真なら `https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/{z}/{x}/{y}.jpg`
    * その他の国土地理院タイルについては https://maps.gsi.go.jp/development/ichiran.html を参照
      
  * OpenStreetMapなら `https://tile.openstreetmap.jp/{z}/{x}/{y}.png`
  * XYZ形式であれば、国土地理院タイル以外の任意のサービスを利用できる(はず)
    
* default: なし

toshow
=======
* type: bool
* Tsutsuji起動時にMaptileを有効化する場合にTrue
* default: False

autozoom
=========
* type: bool
* Tsutsuji起動時にautozoomを有効化する場合にTrue
* default: False
