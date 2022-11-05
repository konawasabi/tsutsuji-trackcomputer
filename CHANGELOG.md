# Change Log

## to be implemented

- solver
  - 渡り線・S字カーブMode
- プロット画面
  - 任意角度への回転
  
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
