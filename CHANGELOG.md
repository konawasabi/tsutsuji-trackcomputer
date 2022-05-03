# Change Log

## to be implemented

- 背景画像関係
  - Reload時に背景画像を再読み込み
  - cfgファイルで背景画像を呼び出せるように
    - @TSUTSUJI_GENERALに背景cfgの項目をつける
  - コントラスト調整
- measure関係
  - Reload/Replot時、relにチェックが入っている場合にオフセットダイアログが開かないようにする
  - relにチェックしてval.実行時、オフセット込みの座標をx,yに表示する
    - @absoluteに自動切り替え？
	- @absoluteカーソルを別カーソル位置基準でオフセットする考え方で、オフセットダイアログに基準カーソル選択ボックスを出す
  - measureボタン押した時にすでにmeasureウィンドウが開かれている場合、トップに持ってくる
  - Reload時に軌道キーリストを書き直す
    - reload時にmeasureウィンドウが開いているとリストが更新されない
	
## [1.1.1] - not released yet

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

[1.1.1]: https://github.com/konawasabi/tsutsuji-trackcomputer/compare/ver1.1.0...ver1.1.1
[1.1.0]: https://github.com/konawasabi/tsutsuji-trackcomputer/compare/v1.0.0...ver1.1.0
