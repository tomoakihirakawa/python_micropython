# Contents
- [🤖サーボモーターの制御](#🤖サーボモーターの制御)
    - [⚙️準備](#⚙️準備)
    - [⚙️例）サーボモーター1つの制御](#⚙️例）サーボモーター1つの制御)
    - [⚙️例）複数のサーボモーターの制御](#⚙️例）複数のサーボモーターの制御)
    - [⚙️ライトヒルのロボットの制御](#⚙️ライトヒルのロボットの制御)


---
# 🤖サーボモーターの制御 

## ⚙️準備 

このディレクトリ`python_micropython/example_ServoMotor`に`lib`をシンボリックリンクで作成しておく．

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

## ⚙️例）サーボモーター1つの制御 

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

---
## ⚙️例）複数のサーボモーターの制御 

やり方は，サーボモーター一つの場合と同じ．
これは，配列にサーボモーターのインスタンスを格納して実行した例．

[./demo1_move_multiple_servos.py#L1](./demo1_move_multiple_servos.py#L1)

---
## ⚙️ライトヒルのロボットの制御 

ライトヒルの曲線に，ロボットの節が乗るようにするためのサーボモーターの角度の計算方法は他の場所で説明している．
ここでは，実査によって得られた角度を各モーターに与えてみる．
やることは，複数のサーボモーターの制御と同じ．

![sample_lighthill.gif](sample_lighthill.gif)

[./demo2_move_multiple_servos_lighthill.py#L1](./demo2_move_multiple_servos_lighthill.py#L1)

---
