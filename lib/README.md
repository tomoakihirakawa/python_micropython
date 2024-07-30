# Contents
- [🤖PWM制御を行うためのPCA9685の使い方](#🤖PWM制御を行うためのPCA9685の使い方)
    - [⚙️PCA9685](#⚙️PCA9685)
        - [🔩PCA9685の周波数を50Hz用に設定する（1/50sに4096のパルスが入るようにprescaleを設定）](#🔩PCA9685の周波数を50Hz用に設定する（1/50sに4096のパルスが入るようにprescaleを設定）)
        - [🔩PWMパルスのオンとオフのタイミングを指定する](#🔩PWMパルスのオンとオフのタイミングを指定する)
            - [🚀 MG996R](#🚀-MG996R)
            - [🚀 DS3218](#🚀-DS3218)
            - [🚀 HS-5086WP](#🚀-HS-5086WP)
- [🤖サーボモーターのクラス](#🤖サーボモーターのクラス)
    - [⚙️MG996R](#⚙️MG996R)
    - [⚙️DS3218](#⚙️DS3218)
    - [⚙️HS-5086WP](#⚙️HS-5086WP)


---
# 🤖PWM制御を行うためのPCA9685の使い方 

## ⚙️PCA9685 

* PWMの周波数を生成するようPCA9685を設定する方法
* デューティーサイクルを決める，PWMパルスのオンとオフのタイミングを指定する方法

### 🔩PCA9685の周波数を50Hz用に設定する（1/50sに4096のパルスが入るようにprescaleを設定） 

PCA9685の内部クロック周波数は25MHz．
PWM周期$`T _{\rm PWM}`$の中に4096個のステップが入るようにprescale, $p$を設定する．
いいかえると，1秒間に$`4096/T _{\rm PWM}=4096 f _{\rm PWM}`$回のステップがはいるようにPCA9685のクロックを設定する．
これには，以下の式を満たすようにprescaleを設定すればよいことがわかる．

```math
\begin{align*}
4096 f _{\rm PWM} &= 25M / (p+1)\\
\rightarrow p &= \frac{25M}{4096 f _{\rm PWM}} - 1
\end{align*}
```

prescaleは整数でなければならないので，`round`で四捨五入する．

### 🔩PWMパルスのオンとオフのタイミングを指定する 

多くの場合，
設定したい[パルス幅[s],角度]の情報をもとに，パルス幅[s]をステップ<4096に変換して，PCA9685に送る．
パルス幅$`\Delta t`$をステップ数に変換するには，

#### 🚀 MG996R 

| パルス幅 (s) | 角度 |
|---|---|
| 1.0 ms | 0° |
| 1.5 ms | 90° |
| 2.0 ms | 180° |

#### 🚀 DS3218 

| パルス幅 (s) | 角度 |
|---|---|
| 0.5 ms | 0° |
| 1.5 ms | 90° |
| 2.5 ms | 180° |

#### 🚀 HS-5086WP 

| パルス幅 (s) | 角度 |
|---|---|
| 0.9 ms | 0° |
| 1.5 ms | 90° |
| 2.1 ms | 180° |

$`4096 * \Delta t / T _{\rm PWM}`$を計算すればよい．

[./PCA9685/PCA9685.py#L1](./PCA9685/PCA9685.py#L1)

---
# 🤖サーボモーターのクラス 

## ⚙️MG996R 

6Vで11kgf-cmのトルクを持つ．
$`\pm 60^\circ`$の範囲で動作する．

PWM周期は20ms，つまり周波数は1/0.02=0.5*10^2=50Hz．

1.5msのパルス幅で中立位置，0.5msで最小角度，2.5msで最大角度．

## ⚙️DS3218 

6Vで20kgf-cmのトルクを持つ．
$`\pm 180^\circ`$または$`\pm 270^\circ`$の範囲で動作する．

PWM周期は2.5ms，つまり周波数は1/0.0025=0.4*10^3=400Hz．

0.5-1.5msのパルス幅で中立位置，0.5-1.0msで最小角度，0.5-2.5msで最大角度．

## ⚙️HS-5086WP 

6Vで2.6kgf-cmのトルクを持つ．
$`\pm 60^\circ`$の範囲で動作する．

PWM周期は20ms，つまり周波数は1/0.02=0.5*10^2=50Hz．

0.9msのパルス幅で中立位置，0.5msで最小角度，2.1msで最大角度．

[./servomotor/servomotor.py#L10](./servomotor/servomotor.py#L10)

---