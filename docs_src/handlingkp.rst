===========
Handling kiloposts
===========

.. image:: ./files/handlingkp.png

inputで指定したmapファイルについて、距離程を書き換えて別ファイルに書き出す機能です。
距離程の書き換え方法は :ref:`ref_handlingkp_mode` に示す4モードから選択できます。
この機能はtsutsujiのメイン機能とは独立して利用できます。

input
-------
距離程を書き換えたいmapファイルを指定します。


output
-------
距離程を書き換えたmapファイルを保存するディレクトリを指定します。

input: `/hoge/fuga/piyo.txt` である場合、デフォルトではoutput: `/hoge/fuga/result/` が指定されます。
新しく作成されたresultディレクトリ以下に、inputで指定したmapファイルと同じ名前のファイルとして変換結果が保存されます。

include要素(ディレクティブ)の扱い
==============================

指定したmapファイルにinclude要素が含まれていた場合、include要素が指定するmapファイルに対しても同様の処理を行い、input側のディレクトリ構成、ファイル名を極力維持して結果を出力します。

ただし、 :ref:`ref_handlingkp_kprange` で距離程範囲を設定していた場合で、include要素の直前の距離程がその範囲外にある場合、そのinclude要素が指定するmapファイルは一切処理されませんので注意してください。

例
++++

Input
~~~~~~~

filepath::

  /hoge/fuga/piyo.txt
  

kilopost range::

  start: 100
  end: 200

  
map::

  0;
  include "foo/bar.txt";

  100;
  include "baz.txt";

  150;
  include "foo/bar/qux.txt";

  300;
  include "foobar.txt";

  
output
~~~~~~~

* 出力されるファイルのディレクトリ構成

  * /hoge/fuga/results
    
    * piyo.txt
    * baz.txt
    * foo/
      
      * bar/

	* qux.txt

* 実行されないinclude要素
  
  * `include "foo/bar.txt";`
  * `include "foobar.txt";`


.. _ref_handlingkp_mode:

Mode
-----

0. echo
==========

* 距離程の書き換えは行わず、inputファイルの内容をそのまま出力する

* 後述の :ref:`ref_handlingkp_kprange` と組み合わせて、特定の距離程範囲にあるマップ要素を抽出する場合に使用できる

実行例
+++++++

Kilopost range::
  
  start: 700
  end: 800

input map::
  
  346;
  Curve.BeginTransition();
  Curve.SetCenter(-1.067/2);
  368;
  Curve.Begin(-200,-0.07);
  370;
  Curve.BeginTransition();
  392;
  Curve.End();

  $foo = 700;
  $foo;
  Curve.BeginTransition();
  Curve.SetCenter(-1.067/2);
  $foo + 22;
  Curve.Begin(-200,-0.07);
  $foo + 24;
  Curve.BeginTransition();
  $foo + 46;
  Curve.End();

  $bar = 894;
  $bar;
  Curve.BeginTransition();
  Curve.SetCenter(1.067/2);
  $bar + 22;
  Curve.Begin(200,0.07);
  $bar + 24;
  Curve.BeginTransition();
  $bar + 46;
  Curve.End();

output map::

  $foo = 700;
  $foo;
  Curve.BeginTransition();
  Curve.SetCenter(-1.067/2);
  $foo + 22;
  Curve.Begin(-200,-0.07);
  $foo + 24;
  Curve.BeginTransition();
  $foo + 46;
  Curve.End();
  $bar = 894;

注意点
++++++

:ref:`ref_handlingkp_kprange` の指定によらず、変数への代入要素(上記例での `$foo = 700;`, `$bar = 894;`)は必ず出力されます。
mapファイルでの変数使用状況によっては、BveTs本体での読み込み時に意図しない結果となる可能性もあるので、距離程に変数を使用しているmapでは出力内容をよく確認することを推奨します。


1. evaluate
============

* 変数、演算子、数学関数で記述された距離程を数値に変換する
  
実行例
+++++++

input map::
  
  $foo = 700;
  $foo;
  Curve.BeginTransition();
  Curve.SetCenter(-1.067/2);
  $foo + 22;
  Curve.Begin(-200,-0.07);
  $foo + 24;
  Curve.BeginTransition();
  $foo + 46;
  Curve.End();
  

output map::

  $foo = 700;
  700.000000;
  Curve.BeginTransition();
  Curve.SetCenter(-1.067/2);
  722.000000;
  Curve.Begin(-200,-0.07);
  724.000000;
  Curve.BeginTransition();
  746.000000;
  Curve.End();

注意点
++++++

距離程から除去された変数 `$foo` への代入要素( `$foo = 700;` ) はそのまま出力されます。


2. new variable
================

* 新しい変数で距離程をオフセットする場合を意図したモード
* 次の要領で距離程の変換を行う

1. inputしたmap先頭に、initializationフィールドに入力した要素を挿入する
2. 距離程を数値に変換する(mode 1と同じ作用)
3. New variable/expressionフィールドに入力した文字列で距離程を書き換える

   * ここで入力した文字列中の `distance` のみ、その時点での距離程数値に置き換えられる

実行例
+++++++

initialization::

  $piyo = 200;

New variable/expression::

  $piyo + distance *2

input map::
  
  $foo = 700;
  $foo;
  Curve.BeginTransition();
  Curve.SetCenter(-1.067/2);
  $foo + 22;
  Curve.Begin(-200,-0.07);
  $foo + 24;
  Curve.BeginTransition();
  $foo + 46;
  Curve.End();

output map::

  # added by kilopost handling
  $piyo = 200;

  $foo = 700;
  $piyo + 700.000000 *2;
  Curve.BeginTransition();
  Curve.SetCenter(-1.067/2);
  $piyo + 722.000000 *2;
  Curve.Begin(-200,-0.07);
  $piyo + 724.000000 *2;
  Curve.BeginTransition();
  $piyo + 746.000000 *2;
  Curve.End();

注意点
++++++

距離程から除去された変数 `$foo` への代入要素( `$foo = 700;` ) はそのまま出力されます。

initialization で新しい変数を定義する場合、変数名はinputファイル中で用いていないものとすることを推奨します。
inputファイル中で用いているものと同じ変数名(ここでは `$foo` )を使うと、inputファイルにある `$foo` への代入要素( `$foo = 700;` )が残っているため予期しない動作をする可能性があります。

New variable/expressionに入力する文字列の末尾には `;` をつけないでください。エラーとなる場合があります。


3. conversion by new example
=============================

* 距離程を定数倍、定数加算する場合を意図したモード
* 次の要領で距離程の変換を行う

1. inputしたmap先頭に、initializationフィールドに入力した要素を挿入する
2. 距離程を数値に変換する(mode 1,2と同じ作用)
3. New variable/expressionフィールドに入力した数式で計算した数値に距離程を書き換える

   * ここで入力する数式としては、BveTs本体で使用できる変数、演算子、数学関数が使用できます。
   * 数式中の `distance` は、その時点での距離程数値となる

実行例
+++++++

initialization::

  $piyo = 200;

New variable/expression::

  $piyo + distance *2

input map::
  
  $foo = 700;
  $foo;
  Curve.BeginTransition();
  Curve.SetCenter(-1.067/2);
  $foo + 22;
  Curve.Begin(-200,-0.07);
  $foo + 24;
  Curve.BeginTransition();
  $foo + 46;
  Curve.End();

output map::

  # added by kilopost handling
  $piyo = 200;

  1600.000000;
  Curve.BeginTransition();
  Curve.SetCenter(-1.067/2);
  1644.000000;
  Curve.Begin(-200,-0.07);
  1648.000000;
  Curve.BeginTransition();
  1692.000000;
  Curve.End();

注意点
++++++

距離程から除去された変数 `$foo` への代入要素( `$foo = 700;` ) はそのまま出力されます。

initialization で新しい変数を定義する場合、変数名はinputファイル中で用いていないものとすることを推奨します。
inputファイル中で用いているものと同じ変数名(ここでは `$foo` )を使うと、inputファイルにある `$foo` への代入要素( `$foo = 700;` )が残っているため本来の意図とは異なる動作をする可能性があります。

New variable/expressionに入力する数式の末尾には `;` をつけないでください。エラーとなる場合があります。

.. _ref_handlingkp_kprange:

Output original kilopost
==========================

チェックが入っている場合、距離程を書き換えるmode 1, 2, 3にて、書き換える前の距離程をコメントとして出力します。
mode 0では何もしません。

実行例
+++++++

mode::

  1. evaluate
  ✅Output original kilopost

input map::
  
  $foo = 700;
  $foo;
  Curve.BeginTransition();
  Curve.SetCenter(-1.067/2);
  $foo + 22;
  Curve.Begin(-200,-0.07);

output map::

  $foo = 700;
  700.000000;# $foo;
  Curve.BeginTransition();
  Curve.SetCenter(-1.067/2);
  722.000000;# $foo + 22;
  Curve.Begin(-200,-0.07);



Sort by kilopost
=================

チェックが入っている場合、読み込んだマップ要素を距離程昇順にソートして出力します。
この機能は全てのmodeに対して有効です。

実行例
+++++++

mode::

  0. echo
  ✅Sort by kilopost

input map::

  $fuga = 500.000000;

  $fuga + 0.00;
  Track['up'].X.Interpolate(-7.00,0.00);
  $fuga + 50.00;
  Track['up'].X.Interpolate(-7.00,-382.66);

  $fuga + 0.00;
  Track['up'].Y.Interpolate(0.00,0.00);
  $fuga + 50.00;
  Track['up'].Y.Interpolate(0.00,0.00);

  $fuga + 50.00;
  Track['up'].Cant.Interpolate(0.000);

  $fuga + 0.00;
  Track['up'].Cant.SetFunction(1);

  $fuga + 0.00;
  Track['up'].Cant.SetGauge(1.067);

output map::

  $fuga = 500.000000;

  $fuga + 0.00;
  Track['up'].X.Interpolate(-7.00,0.00);
  Track['up'].Y.Interpolate(0.00,0.00);
  Track['up'].Cant.SetFunction(1);

  Track['up'].Cant.SetGauge(1.067);


  $fuga + 50.00;
  Track['up'].X.Interpolate(-7.00,-382.66);

  Track['up'].Y.Interpolate(0.00,0.00);

  Track['up'].Cant.Interpolate(0.000);

  Track['up'].Cant.SetCenter(-0.533);

注意点
++++++

mode 2では書き換え前の距離程値に従ってソートを行い、mode 3では書き換え後の値によってソートを行います。
入力マップファイルとNew variable/expressionの内容によっては予想と異なるソート結果を得る可能性があります。

Kilopost range
---------------
変換処理を行い、ファイルへ書き出す距離程の下限、上限を設定します。
ここでの距離程は、変換前の値（inputで指定したmapファイルの値）を指します。
全てのモードでKilopost rangeの指定は有効です。

start
======
チェックを入れると、 `距離程 >= startの値` の要素についてのみoutputファイルへ出力します。
これより手前にある要素はoutputファイルへ出力されません。 **(変数への代入要素を除く)**

チェックボックスが空の場合、距離程の下限は設定されません。

end
====
チェックを入れると、 `距離程 <= endの値` の要素についてのみoutputファイルへ出力します。
これより後ろにある要素はoutputファイルへ出力されません。 **(変数への代入要素を除く)**

チェックボックスが空の場合、距離程の上限は設定されません。

Search
-------

チェックを入れると、Searchフィールドの文字列が含まれるマップ要素のみを抽出してファイルを書き出します。

Regular expressionにチェックが入っている場合は、Searchフィールドの文字列を `正規表現 <https://docs.python.org/ja/3/library/re.html#regular-expression-syntax>`__ と解釈して、条件に合致するマップ要素を抽出します。

この機能は上記全てのmode, オプションに対して有効です。

注意点
=======

1. コメント要素、変数への代入要素、include要素はSearch文字列の内容によらず必ず出力されます。
2. Regular expressionをチェックしていない場合、Search文字列での大文字、小文字の区別は無視されます。
3. Sort by kilopostをチェックしていない場合、入力マップファイルの内容によっては距離程要素のみが出力される場合があります。

3.の例
++++++

mode::

  0. echo
  🟩Sort by kilopost
  ✅Search, 🟩Regular expression

search::
  
  Track['up'].Y

input map::

  $fuga = 500.000000;

  $fuga + 0.00;
  Track['up'].X.Interpolate(-7.00,0.00);
  $fuga + 50.00;
  Track['up'].X.Interpolate(-7.00,-382.66);

  $fuga + 0.00;
  Track['up'].Y.Interpolate(0.00,0.00);
  $fuga + 50.00;
  Track['up'].Y.Interpolate(0.00,0.00);

  $fuga + 50.00;
  Track['up'].Cant.Interpolate(0.000);

  $fuga + 0.00;
  Track['up'].Cant.SetFunction(1);

  $fuga + 0.00;
  Track['up'].Cant.SetGauge(1.067);

output map::
  
  $fuga = 500.000000;

  $fuga + 0.00;
  $fuga + 50.00;

  $fuga + 0.00;
  Track['up'].Y.Interpolate(0.00,0.00);
  $fuga + 50.00;
  Track['up'].Y.Interpolate(0.00,0.00);

  $fuga + 50.00;

  $fuga + 0.00;

  $fuga + 0.00;


Do It
-------
上記の設定に基づいて、outputで指定したディレクトリへファイルを出力します。
