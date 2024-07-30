'''DOC_EXTRACT 0_0_servomotor

# サーボモーターの制御

## 準備

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

## 例）サーボモーター1つの制御

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

'''

from lib.servomotor import *
from time import sleep, time_ns
import math

s = servomotor(0, 0)
s.setDegree(90)
start = time_ns()

while True:
    t = 2*(time_ns() - start)*10**-9
    s.setDegree(90+50*math.sin(t))
    sleep(0.001)
