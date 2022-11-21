=================
honsen_down の構築
=================

始点を決める
============

honsen_down軌道の始点座標を求め、main.cfgに[honsen_down]セクションを追加する。

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

富山寄り分岐器
==============

tateyama_upとの分岐器、honsen_upとの分岐器共に直進方向なので、特に処理は行わない。

プラットホーム部
===============

プラットホーム部分の曲線軌道は複心曲線（異なる半径を持つ複数の円軌道からなる曲線）と想像されるが、詳細なデータを空中写真のみから得ることは難しいため、ここでは次のように ***誤魔化す*** 処理する。
正確な曲線を得るためには、現地での曲線標の調査が必要だろう。

1. カーソルAのtrackをtateyama_downにセットする
2. カーソルAの位置、方向を曲線始点にセットする

   - ここでは距離程84.0m

3. カーソルBのtrackを @absoluteにセットする
4. カーソルBの位置、方向をプラットホーム中央あたりの軌道中心にセットする
5. CurveTrack Solverを以下の設定にしてDo Itする

   - α: A, β: B
   - mapsyntax にチェック
   - Mode: 1. α(fix)->β(free), R(free)

6. ターミナルへの出力をhonsen_down.txtにコピーする

   - .. code-block:: text
         :caption: tateyama_down.txt

	 ...
	 $pt_a = 84.000000;
	 $pt_a;
	 $cant = 0;
	 Curve.SetFunction(1);
	 Curve.Interpolate(0.000000,0);
	 $pt_a +0.000000;
	 Curve.Interpolate(-176.237575, $cant);
	 $pt_a +94.979259;
	 Curve.Interpolate(-176.237575, $cant);
	 $pt_a +94.979259;
	 Curve.Interpolate(0.000000,0);

7. 
