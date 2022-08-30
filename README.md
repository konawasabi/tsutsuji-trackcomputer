# Tsutsuji TrackComputer

Bve trainsim 5/6向けマップファイルの制作支援Pythonスクリプトです。
全ての軌道を自軌道構文で記述し、一つの軌道を基準とした他軌道構文に変換するのが主な機能です。
まだ開発途上ですが、軌道データ作成に役立つ測量機能も付属しています。

## インストール

動作に必要な環境

- [Python 3](https://www.python.org/downloads/)
- [Kobushi trackviewer](https://github.com/konawasabi/kobushi-trackviewer) Ver1.1.3以降
- [numpy](https://numpy.org)
- [matplotlib](https://matplotlib.org)
- [scipy](https://www.scipy.org)
- [lark](https://lark-parser.readthedocs.io/en/latest/)
- [ttkwidgets](https://ttkwidgets.readthedocs.io/en/latest/)
- [requests](https://requests-docs-ja.readthedocs.io/en/latest/)

インストールするには、Python 3をインストールしてからPowershellで次のコマンドを実行してください。
Tsutsuji本体と、動作に必要なパッケージが自動でインストールされます。
```
pip install tsutsuji-trackcomputer
```

なお、https://konawasabi.riceball.jp/2022/06/01/tsutsuji-kobushi-installguide/ にて、Python3のセットアップを含めたインストール手順の説明をしていますので、参考にしてもらえればと思います。

インストール済みのTsutsujiをバージョンアップする際は、次のコマンドを実行してください。
```
pip install --upgrade tsutsuji-trackcomputer
```

## 起動

Tsutsujiは次のコマンドで起動できます。

```
python -m tsutsuji
```

読み込むcfgファイルを予め指定するときは、以下のコマンドを実行します。

```
python -m tsutsuji hoge.cfg
```

### 非対話モード

`-n`オプションをつけて実行すると、Tsutsujiを非対話モードで実行できます。

非対話モードでは、指定したcfgファイルの内容に基づいて他軌道データを生成し、そのまま終了します。このときGUIは起動しません。

```
python -m tsutsuji -n hoge.cfg
```

## Documents

https://konawasabi.github.io/tsutsuji-trackcomputer/


## License

[Apache License, Version 2.0](LICENSE)

## 重要事項

本プログラムの著作権は[konawasabi](#Contact) (以下、作者)が有します。

本プログラムについて作者はいかなる保証もせず、またプログラムを実行して生じた結果についての責任を負いません。

Apache Licence, Version 2.0に従う限り、本ソフトウェアの改変、再配布を自由に行うことができます。

## Acknowledgements

* 緯度経度->直交座標への変換ルーチンとして、下記URLにて公開されているsw1227氏のコードを使用させていただきました
  * https://qiita.com/sw1227/items/e7a590994ad7dcd0e8ab

## Contact

Author: Konawasabi

Mail: webmaster@konawasabi.riceball.jp

Website: https://konawasabi.riceball.jp/
