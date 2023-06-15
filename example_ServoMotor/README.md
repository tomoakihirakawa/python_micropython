# Contents

- [🤖サーボモーターの制御](#🤖サーボモーターの制御)
    - [⚙️準備](#⚙️準備)
    - [⚙️サーボモーター1つの制御](#⚙️サーボモーター1つの制御)
    - [⚙️複数のサーボモーターの制御](#⚙️複数のサーボモーターの制御)


---
# 🤖サーボモーターの制御 

## ⚙️準備 

このディレクトリに`lib`をシンボリックリンクで作成しておく．

```
ln -s ../lib ./lib
```

下の方法で`lib`内の`servomotor`ディレクトリのファイルをインポートできる．

```
from lib.servomotor import *
```

上の命令で`lib`内の`servomotor`ディレクトリにある`__init__.py`が実行される．

`__init__.py`には，`from .servomotor import *`という命令が書かれている．
この意味は，`lib`内の`servomotor`内の`servomotor.py`に書かれている関数やクラスを全てインポートするという意味である．
これで，`servomotor.py`内の`servomotor`クラスを使うことができる．

このservomotorクラスは，`servomotor(チャンネル, オフセット角度)`で初期化する．
例えば，以下のようにすると，チャンネル0のサーボモーターを初期角度90度で初期化できる．

```
s = servomotor(0, 90)
```

角度を変更するには，`setDegree`を使う．例えば，以下のようにすると，チャンネル0のサーボモーターの角度を180度に変更できる．

```
s.setDegree(180)
```

[../lib/servomotor/servomotor.py#L10](../lib/servomotor/servomotor.py#L10)



## ⚙️サーボモーター1つの制御 

<details>

---

<summary>Python パッケージ</summary>

あるディレクトリに，`__init__.py`というファイルがあると，そのディレクトリは**Pythonのパッケージ**となる．

```
from パッケージ名 import *
```

とすることで，そのパッケージ内の`__init__.py`がまず実行され，それに従って，パッケージ内のモジュールがインポートされる．
ここでは，`lib.servomotor`をパッケージとしてインポートしている．

---

</details>

ここでは，以下のようにインポートしたが

```
from lib.servomotor import *
```

`lib/servomotor/servomotor.py`から`servomotor`クラスをインポートする，という意味で，次のようにもできる．
これで同じように`s = servomotor(0, 90)`としてサーボモーターを作成できる．

```
from lib.servomotor.servomotor import servomotor
```

![](sample.gif)


[./demo0_move_servo.py#L1](./demo0_move_servo.py#L1)


## ⚙️複数のサーボモーターの制御 

やり方は，サーボモーター一つの場合と同じ．
これは，配列にサーボモーターのインスタンスを格納して実行した例．


[./demo1_move_multiple_servos.py#L1](./demo1_move_multiple_servos.py#L1)


---
