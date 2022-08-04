.. tsutsuji documentation master file, created by konawasabi
   sphinx-quickstart on Fri Mar 18 23:41:00 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

====================================
Documents for Tsutsuji trackcomputer
====================================

Introduction
-------------

Tsutsuji trackcomputerは、Bve Trainsim 5/6向けマップファイルの制作を支援するPythonスクリプトです。

全ての軌道を自軌道構文(Curve, Gradient)で構築し、そのうち1つの軌道を基準とした他軌道構文(Track.X, Track.Y, etc.)に変換することを主な目的としています。

他軌道構文への変換では、軌道座標に加えて

* 平面曲線／縦曲線相対半径
* 緩和曲線
* カント
* カント回転中心
  
の変換も行います。

まずは :doc:`Tutorial 基本機能 <tutorial_first>` をご覧ください。

Contents
---------

.. toctree::
   :maxdepth: 2

   tutorial
   referenceguide
   tsutsuji API (Under construction) <tsutsuji>

Repository
-----------
  
* https://github.com/konawasabi/tsutsuji-trackcomputer


Acknowledgements
-----------------

* 緯度経度->直交座標への変換ルーチンとして、下記URLにて公開されているsw1227氏のコードを使用させていただいています
  
  * https://qiita.com/sw1227/items/e7a590994ad7dcd0e8ab

