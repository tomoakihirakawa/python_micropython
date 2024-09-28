'''DOC_EXTRACT 3_0_servomotor

# 魚ロボット

ライトヒルの曲線に，ロボットの節が乗るようにするためのサーボモーターの角度の計算方法は他の場所で説明している．
ここでは，実査によって得られた角度を各モーターに与えてみる．やることは，複数のサーボモーターの制御と同じ．

<img src="sample_lighthill.gif" width="600px">

## 無線魚ロボットの操作方法

### 事前準備

* PCA9685のどのチャンネルにどのサーボモーターが接続されているかを確認しておく．
* 予めラズパイゼロは，`>*))))><`というSSIDのルーターに接続しておく．以下では，ラズパイゼロには，ルーターから，IPアドレス`192.168.0.9`が割り当てられたとする．
* PC（ラズパイゼロのpythonプログラムを編集するためのPC）も，同じルーターに接続しておく．

<img src="robotic_fish.png" width="600px">

<img src="robotic_fish_howtocontrol.png" width="600px">

### 効率的な開発方法（VSCodeでラズパイのプログラムを編集して，ターミナルで実行）

過去のマウントを解除して，再度マウントする．

```sh
umount -f /Volumes/pi19216809
sshfs pi@192.168.0.9:/home/pi /Volumes/pi19216809
```

マウントしたディレクトリに移動して，VSCodeを起動する．

```sh
cd /Volumes/pi19216809/research/example_ServoMotor/
code ./
```

<img src="sshfs_and_code.png" width="600px">

VSCodeのターミナルで，`ssh`でラズパイにログインする．

```sh
ssh pi@192.168.0.9
cd research/example_ServoMotor/
```

<img src="sshfs_and_code_ssh_cd.png" width="600px">

これで，VSCodeでラズパイのプログラムを編集して，ターミナルで実行することができる．実行例は次の通り．

```sh
python3 servomotor_HS5086WP.py 
```

ターミナルでラズパイの電源を切るときは，次を実行する．

```sh
sudo shutdown now
```

'''

from lib.servomotor import *
from lib.PCA9685 import *
import time
import math

pwm = PCA9685(0x40)
pwm.set_pwm_freq(50)
servo = [HS5086WP(12,pwm),HS5086WP(4,pwm)]
time.sleep(0.1)
servo[0].setDegree(0)
servo[1].setDegree(0)
time.sleep(0.1)# 開始時間を取得
start_time = time.time()
while True:
    # 現在の時刻を取得し、tとして使う
    t = time.time() - start_time  # 経過時間 t (秒)

    T = 0.5 # 周期
    w = 2. * math.pi / T  # 角周波数
    dt = 0
    theta1 = 15 * math.sin(w * t)  # サーボ1の角度
    theta2 = 25 * math.sin(w * (t-dt))  # サーボ2の角度

    servo[0].setDegree(theta1)
    servo[1].setDegree(theta2)
    
    print(theta1, theta2)
    
    time.sleep(0.02)  # 10ミリ秒待つ
