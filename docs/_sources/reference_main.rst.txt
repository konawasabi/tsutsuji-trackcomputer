===============
メインウィンドウ
===============

.. image:: ./files/mainwindow.png
	   :scale: 60%

Replotボタン
-------------

プロットウィンドウの再描画を行います。

Plot controlセクションの設定を変更した場合、Replotを実行すると変更がプロットウィンドウに反映されます。

Plot control
--------------

* x, y

  * プロットの中心座標を指定する
  * 単位は[m]

* scale

  * x軸方向の表示範囲を指定する
  * 単位は[m]
  * デフォルトは1000 m

* Y. Mag.

  * x軸方向に対するy軸方向の拡大率を指定する
  * デフォルトは1

* ↑↓←→ボタン

  * 矢印の方向に表示範囲を移動する

* Symbols

  * radius

    * Curve要素が指定されている座標にマーカー(●)を描画する

  * gradient

    * Gradient要素が指定されている座標にマーカー(▲)を描画する

  * supplemental_cp

    * supplemental_cpが指定されている座標にマーカー(✖)を描画する


Measureボタン
-------------

Measureウィンドウを開きます。
詳細は :doc:`reference_measure` を参照。

.. image:: ./files/measure.png
	   :scale: 60%

Generateボタン
--------------

cfgファイルの設定に従い、他軌道構文データを計算します。
計算結果は、cfgファイル[@TSUTSUJI_GENERAL]セクションのoutput_pathで指定したディレクトリに出力されます。
デフォルトでは、cfgファイルと同じ階層のresultディレクトリへ保存されます。

これと同時に、計算した他軌道の線形をプロットウィンドウに表示します。
計算結果は黒線でプロットされます。
軌道カラーはTrackウィンドウで変更できます。
