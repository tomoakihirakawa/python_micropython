# Contents
- [🤖サーボモーターの制御](#🤖サーボモーターの制御)
    - [⚙️準備](#⚙️準備)
        - [🔩🔩servomotorクラス](#🔩🔩servomotorクラス)
        - [🔩🔩MG996R](#🔩🔩MG996R)
    - [⚙️⚙️PCA9685](#⚙️⚙️PCA9685)
        - [🔩🔩50Hzを作る](#🔩🔩50Hzを作る)
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

### 🔩🔩servomotorクラス  

このservomotorクラスは，`servomotor(チャンネル, オフセット角度)`で初期化する．
例えば，以下のようにすると，チャンネル0のサーボモーターを初期角度90度で初期化できる．

```
s = servomotor(0, 90)
```

角度を変更するには，`setDegree`を使う．例えば，以下のようにすると，チャンネル0のサーボモーターの角度を180度に変更できる．

```
s.setDegree(180)
```

### 🔩🔩MG996R  

6Vで11kgf-cmのトルクを持つ．
$`\plusmn 60^\circ`$の範囲で動作する．

PWM周期は20ms，つまり周波数は1/20=50Hz．

1.5msのパルス幅で中立位置，0.5msで最小角度，2.5msで最大角度．
[../lib/servomotor/servomotor20240730.py#L10](../lib/servomotor/servomotor20240730.py#L10)


## ⚙️⚙️PCA9685  

* PWMの周波数を生成するようPCA9685を設定する方法
* デューティーサイクルを決める，PWMパルスのオンとオフのタイミングを指定する方法

### 🔩🔩50Hzを作る  

PCA9685の内部クロック周波数は25MHz．
PWM周期$`T _{\rm PWM}`$の中に4096個のステップが入るようにprescaleを設定する．
いいかえると，1秒間に$`4096/T _{\rm PWM}=4096 f _{\rm PWM}`$回のステップがはいるようにPCA9685のクロックを設定する．
これには，以下の式を満たすようにprescaleを設定すればよいことがわかる．

```math
\begin{align*}
4096 f _{\rm PWM} &= 25M / (prescale+1)\\
\rightarrow prescale &= \frac{25M}{4096 f _{\rm PWM}} - 1
\end{align*}
```
[../lib/PCA9685/PCA9685.py#L1](../lib/PCA9685/PCA9685.py#L1)


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
