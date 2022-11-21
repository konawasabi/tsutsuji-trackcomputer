=================
honsen_up の構築
=================

始点を決める
============

honsen_up軌道の始点座標を求め、main.cfgに[honsen_down]セクションを追加する。

1. カーソルAのtrackをtateyama_upにセットする
2. カーソルAを立山寄り分岐器の始端にセットし、その地点の距離程を読む

   - ここでは438m
     
3. 下記の内容でmain.cfgに[tateyama_down]セクションを追加する
   
   - 始点はtateyama_up軌道の距離程438m地点での値と同一、向きはtateyama_upと180°反対方向に設定される
   - .. code-block:: text
         :caption: main.cfg

	 ...
	 [honsen_down]
	 file = honsen_down.txt
	 absolute_coordinate = False
	 parent_track = tateyama_up
	 origin_kilopost = 438
	 x = 0
	 y = 0
	 z = 0
	 angle = -180
	 endpoint = 1500

4. main.cfgと同じディレクトリに以下の内容でhonsen_down.txtを作成する

   - .. code-block:: text
	 :caption: honsen_down.txt

	 BveTs Map 2.02:utf-8

	 0;
	 Curve.SetGauge(1.067);
	 Curve.SetFunction(0);
