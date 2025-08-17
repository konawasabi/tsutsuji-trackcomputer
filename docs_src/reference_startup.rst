===============
起動方法
===============

Tsutsuji を起動するには、Windowsの場合はPowershellで次のコマンドを実行します。

`python -m tsutsuji`

読み込むcfgファイルを予め指定するときは、以下のコマンドを実行します。

`python -m tsutsuji hoge.cfg`

非対話モード
-----------

`-n` オプションをつけて実行すると、Tsutsujiを非対話モードで実行できます。

`python -m tsutsuji -n hoge.cfg`

非対話モードでは、指定したcfgファイルの内容に基づいて他軌道データを生成し、そのまま終了します。（Generateを実行した場合と同じ結果が得られる）
このときGUIは起動しません。

計算時間表示モード
------------------

`-t` オプションをつけて実行すると、:ref:`Generate <ref_main_generate>` 実行時に処理に要した時間を秒単位でターミナルへ表示します。

`python -m tsutsuji -t hoge.cfg`
