'''DOC_EXTRACT servomotor

# サーボモーターの制御

## 準備

このディレクトリに`lib`をシンボリックリンクで作成しておく．

```
ln -s ../lib ./lib
```

下の方法で`lib`内の`servomotor`ディレクトリのファイルをインポートできる．

```
from lib.servomotor import *
```

上の命令で`lib`内の`servomotor`ディレクトリにある`__init__.py`が実行される．
`__init__.py`には，`from .servomotor import *`という命令が書かれており，
`lib`内の`servomotor`内の`servomotor.py`に書かれている関数やクラスが，そのまま使えるようになる．

\insert{servomotor_calss}

## サーボモーター1つの制御

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
