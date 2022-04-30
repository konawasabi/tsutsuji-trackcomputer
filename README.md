# Tsutsuji TrackComputer

Bve trainsim 5/6向けマップファイルの制作支援Pythonスクリプトです。
全ての軌道を自軌道構文で記述し、一つの軌道を基準とした他軌道構文に変換するのが主な機能です。
まだ未完成ですが、軌道データ作成に役立つ測量機能も付属しています。

## インストール

動作に必要な環境

- Python 3.x
- [Kobushi trackviewer](https://github.com/konawasabi/kobushi-trackviewer) Ver1.1.2以降
- [numpy](https://numpy.org)
- [matplotlib](https://matplotlib.org)
- [scipy](https://www.scipy.org)
- [lark](https://lark-parser.readthedocs.io/en/latest/)
- [ttkwidgets](https://ttkwidgets.readthedocs.io/en/latest/)

インストールするには、Python3をインストールしてからPowershellで次のコマンドを実行してください。
Tsutsuji本体と、動作に必要なパッケージが自動でインストールされます。

```
pip install tsutsuji-trackcomputer
```

インストール済みのTsutsujiをバージョンアップする際は、`pip install -U tsutsuji-trackcomputer`を実行してください。


Tsutsujiは次のコマンドで起動できます。

```
python -m tsutsuji
```

## Documents

https://konawasabi.github.io/tsutsuji-trackcomputer/


## License

[Apache License, Version 2.0](LICENSE)

## 重要事項

本プログラムの著作権は[konawasabi](#Contact) (以下、作者)が有します。

本プログラムについて作者はいかなる保証もせず、またプログラムを実行して生じた結果についての責任を負いません。

Apache Licence, Version 2.0に従う限り、本ソフトウェアの改変、再配布を自由に行うことができます。

## Contact

Author: Konawasabi

Mail: webmaster@konawasabi.riceball.jp

Website: https://konawasabi.riceball.jp/
