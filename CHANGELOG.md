# Change Log

## to be implemented

- プロット画面
  - 任意角度への回転
  
## [1.7.5] - 2024-07-28

- matplotlib ver 3.9.0以降がインストールされている環境でMeasure, pos.カーソルが正常動作するように修正
- CuveTrack Solver
  - Mode 4,5にてAssign result to cursorを有効にした場合、対象となるカーソルのTrackが@absolute以外に指定されていた場合の挙動を変更
	- これまでは、計算結果が対象カーソルに反映されなかった
	- 本バージョンからは、計算結果（カーソル座標と方位）を対象カーソルに反映の上、Track: @absoluteに上書きする
  
## [1.7.4.1] - 2024-06-19

- matplotlib ver. 3.9.0 がインストールされている環境下でMeasure, pos.カーソルが正常動作しない問題の暫定処置
  - matlplotlibの要求バージョンの上限を3.8.4に設定
  - tsutsuji本体のコードは変更なし
  
## [1.7.4] - 2023-11-19

- ver. 1.7.3で追加した処理のバグフィックス
  - 自軌道法線と対象軌道が2回交差する場合の処理が正しく動作しない問題を修正
- [@TSUTSUJI_GENERAL]セクションのcheck_u = Falseでは、ver. 1.7.2以前の処理のみを実行
  - 処理時間が増加したため、2回交差の可能性が少ない場合は処理を省略できるようにしている
  
## [1.7.3] - 2023-11-11

- 自軌道に対する各軌道の相対座標計算ルーチンの修正
  - 自軌道法線と対象軌道が2回交差する場合、自軌道から近い方の交点を検出するように変更
  - 2回交差を判別する処理を実行するかどうかはcfgファイル、[@TSUTSUJI_GENERAL]セクションのcheck_uで指定
	- デフォルトではTrue (実行する)
- マップファイルとして出力される各パラメータ桁数の変更に対応
  - cfgファイル、[@TSUTSUJI_GENERAL]セクションのoutput_digitで指定
  - デフォルトでは小数点以下3桁
  
## [1.7.2] - 2023-09-18

- プロット画面のウィンドウリサイズへの対応
  - ウィンドウリサイズ後、プロット範囲を再描画するにはReplotを実行する

## [1.7.1] - 2023-06-25
- Trackウィンドウでgenerateした軌道を制御できないバグを修正

## [1.7.0] - 2023-06-25

- Track構文で定義した他軌道データの読み込み、変換に対応
- Measure
  - x, y, dir, distの有効数字を小数点以下3桁に変更
  - 各種ウィジェットのサイズ修正
  - nearesttrackの軌道選択メニューについて、マップリロード時に内容を更新

## [1.6.1] - 2023-05-21

- offset_variable関係
  - offset_variableを適用したデータをgenerateした時、変換結果がプロットウィンドウに正しく表示されるよう修正
  - 自軌道データで、distance変数を参照している距離程については、offset_variableを適用しないように修正
- 一度に大量(>36枚)のマップタイルを取得する場合に確認ダイアログを表示

## [1.6.0] - 2023-05-06

- Curvetrack Solver
  - 反向曲線、複心曲線向けModeを追加
    - Mode 3-2, 8-1, 8-2, 9-1, 9-2, 9-3
  
## [1.5.4] - 2023-03-19

- Curvetrack Solver
  - 計算結果をプロットする際に、軌道始点or終点が表示されない問題を修正
  - Mode2で TCLα, β>0 の場合、自軌道構文が正しく出力されない問題を修正
  
## [1.5.3] - 2023-01-29

- generate実行時の"too many indices ..."エラーに対する処理を追加
   - メッセージ `{trackkey}: IndexError. Generate has been ignored.` を出力して、その軌道に対するファイル出力をスキップ
   - 当該エラーは、owntrack基準の座標系で表せられない位置にある軌道を計算した時に発生
      - owntrack終点より先に始点がある軌道
	  - Track構文で表すことができない
  
## [1.5.2] - 2022-11-14

- Curvetrack Solver Mode 7にて自軌道構文が正しく出力されない問題を修正
  
## [1.5.1] - 2022-11-05

- cfgファイルの読み込み時にエンコーディングを明示
  - 日本語が含まれている場合にエンコーディングが正しく選択されない問題を修正
  - デフォルトではutf-8を期待し、デコードに失敗した場合はcp932で再読み込みを試みる
  
## [1.5.0] - 2022-10-16

- 自軌道マップデータに対するoffset_variableの適用
  - generateすると自軌道データの距離程を `$offset_variable + distance;` の形式に変換してファイルへ出力
  
## [1.4.1] - 2022-08-30

- Maptile
  - Backimgの背後にMaptileを描画するように変更
  - toshowパラメータをcfgファイルで設定可能に変更
  - オートズームレベル設定の追加
  - 画像データをbackimgとしてエクスポート
  - デフォルトパラメータ設定ルーチンの修正
  - Maptile...メニューにキーショートカット追加(CTRL+T)
- Measure
  - 軌道に拘束されているカーソルに対してRel.にチェックしてVal.実行した場合に、ReplotするとVal.実行結果がキャンセルされる挙動を修正

## [1.4.0] - 2022-08-27


- 地理院地図との連携(Maptile)
  - 現在のプロット画面を含むマップタイルを取得し表示する
  - XYZ地図タイル形式であれば、地理院地図に限らず表示可能(のはず)
  
## [1.3.1] - 2022-08-08

- Curvetrack Solver
  - 始点マーカーの距離程を印字
- UI関係
  - backimg
    - ウィンドウの多重オープン防止
	- タブフォーカス移動順序の修正
  - Generateボタンの配置を改善

## [1.3.0] - 2022-08-04

- kml/csvファイルから軌道データを読み込む
  - Measure機能による各種測定
  - 他軌道としてgenerate
- Curvetrack Solver
  - 緩和曲線長の最適化モードを追加(Mode 6, 7)
- 起動時にプロットウィンドウのスケールを自動設定

## [1.2.0] - 2022-05-30

- track上の距離程でカーソル座標、軌道原点座標を指定する場合、unit_lengthの倍数でない距離程を指定した場合は前後の点から内挿して求めた座標を設定する
- 曲線半径ソルバーに計算モード4, 5を追加
  - (4) 起点、曲線半径、曲線長を固定して終点座標を算出
  - (5) 終点、曲線半径、曲線長を固定して起点座標を算出
- 非対話モードの実装
  - -nオプションをつけて起動するとguiを開かずに変換処理だけ行う
- 各軌道の制御点を種類別に表示
  - curve, gradient, supplemental_cpの3種類
- direction設定時の接線をreplot時に再描画
- trackウィンドウの実装
  - trackごとのプロットOn/Off
  - trackカラーの変更
- generateした結果をプロット
- キーアサインの追加
  - ReturnキーでReplot実行
  - Shift+カーソルキーでプロット範囲を移動
  
## [1.1.3] - 2022-05-11

- 相対半径算出ルーチンの修正
  - 相対座標を線形補間してから曲率を計算する
- direction設定時に表示する接線を重複して描画しないように修正
  
## [1.1.2] - 2022-05-08

- 多くの場合に他軌道のカント構文が出力されないバグの修正
- measure関係
  - direction設定時の接線挙動を修正
    - trackに@absoluteが指定されている時のみ表示する
  - カーソルがプロットウィンドウ外に出た時のエラー処理
  - 曲線半径ソルバーの構文出力をInterpolateベースに変更

	
## [1.1.1] - 2022-05-07

- 背景画像関係
  - Reload時に背景画像を再読み込み
  - 線形データcfgファイル読み込み時に背景画像cfgファイルを同時読み込み
- measure関係
  - Reload時に軌道キーリストを書き直す
  - measureボタン押した時にすでにmeasureウィンドウが開かれている場合、トップに持ってくる
  - relにチェックしてval.実行後、relのチェックを解除する
  - direction設定時に接線を表示する
  
## [1.1.0] - 2022-05-01

- 別軌道に従属した座標系で軌道原点を表す
- プロット画面
  - 表示位置の移動ボタンを追加
  - アスペクト比を可変に
- 計測機能の修正、追加
  - 2カーソル間の角度算出ルーチンの修正
  - 曲線半径ソルバー
    - 計算モードを追加
      1. 起点固定、終点フリー、半径を算出
	  1. 起点フリー、終点固定、半径を算出
	  1. 起点フリー、終点フリー、半径固定
	- 計算結果をcurve構文で出力
  - カーソル設定時のウィンドウ自動切り替え
  - カーソルC,Dを追加
  - 任意のカーソルに対して距離,角度,軌道までの最短距離の測定、平行,垂直方向距離の測定を実行可能に
- 背景画像
  - 設定ウィンドウの整理
  - 設定のsave/loadに対応

## 1.0.0 - 2022-04-09

- 1st release

[1.7.5]: https://github.com/konawasabi/tsutsuji-trackcomputer/compare/ver1.7.4.1...ver1.7.5
[1.7.4.1]: https://github.com/konawasabi/tsutsuji-trackcomputer/compare/ver1.7.4...ver1.7.4.1
[1.7.4]: https://github.com/konawasabi/tsutsuji-trackcomputer/compare/ver1.7.3...ver1.7.4
[1.7.3]: https://github.com/konawasabi/tsutsuji-trackcomputer/compare/ver1.7.2...ver1.7.3
[1.7.2]: https://github.com/konawasabi/tsutsuji-trackcomputer/compare/ver1.7.1...ver1.7.2
[1.7.1]: https://github.com/konawasabi/tsutsuji-trackcomputer/compare/ver1.7.0...ver1.7.1
[1.7.0]: https://github.com/konawasabi/tsutsuji-trackcomputer/compare/ver1.6.1...ver1.7.0
[1.6.1]: https://github.com/konawasabi/tsutsuji-trackcomputer/compare/ver1.6.0...ver1.6.1
[1.6.0]: https://github.com/konawasabi/tsutsuji-trackcomputer/compare/ver1.5.4...ver1.6.0
[1.5.4]: https://github.com/konawasabi/tsutsuji-trackcomputer/compare/ver1.5.3...ver1.5.4
[1.5.3]: https://github.com/konawasabi/tsutsuji-trackcomputer/compare/ver1.5.2...ver1.5.3
[1.5.2]: https://github.com/konawasabi/tsutsuji-trackcomputer/compare/ver1.5.1...ver1.5.2
[1.5.1]: https://github.com/konawasabi/tsutsuji-trackcomputer/compare/ver1.5.0...ver1.5.1
[1.5.0]: https://github.com/konawasabi/tsutsuji-trackcomputer/compare/ver1.4.1...ver1.5.0
[1.4.1]: https://github.com/konawasabi/tsutsuji-trackcomputer/compare/ver1.4.0...ver1.4.1
[1.4.0]: https://github.com/konawasabi/tsutsuji-trackcomputer/compare/ver1.3.1...ver1.4.0
[1.3.1]: https://github.com/konawasabi/tsutsuji-trackcomputer/compare/ver1.3.0...ver1.3.1
[1.3.0]: https://github.com/konawasabi/tsutsuji-trackcomputer/compare/ver1.2.0...ver1.3.0
[1.2.0]: https://github.com/konawasabi/tsutsuji-trackcomputer/compare/ver1.1.3...ver1.2.0
[1.1.3]: https://github.com/konawasabi/tsutsuji-trackcomputer/compare/ver1.1.2...ver1.1.3
[1.1.2]: https://github.com/konawasabi/tsutsuji-trackcomputer/compare/ver1.1.1...ver1.1.2
[1.1.1]: https://github.com/konawasabi/tsutsuji-trackcomputer/compare/ver1.1.0...ver1.1.1
[1.1.0]: https://github.com/konawasabi/tsutsuji-trackcomputer/compare/v1.0.0...ver1.1.0
