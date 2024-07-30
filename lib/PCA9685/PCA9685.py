'''DOC_EXTRACT PCA9685

# PWM制御を行うためのPCA9685の使い方

## PCA9685

* PWMの周波数を生成するようPCA9685を設定する方法
* デューティーサイクルを決める，PWMパルスのオンとオフのタイミングを指定する方法

### PCA9685の周波数を50Hz用に設定する（1/50sに4096のパルスが入るようにprescaleを設定）

PCA9685の内部クロック周波数は25MHz．
PWM周期$`T_{\rm PWM}`$の中に4096個のステップが入るようにprescale, $p$を設定する．
いいかえると，1秒間に$`4096/T_{\rm PWM}=4096 f_{\rm PWM}`$回のステップがはいるようにPCA9685のクロックを設定する．
これには，以下の式を満たすようにprescaleを設定すればよいことがわかる．

```math
\begin{align*}
4096 f_{\rm PWM} &= 25M / (p+1)\\
\rightarrow p &= \frac{25M}{4096 f_{\rm PWM}} - 1
\end{align*}
```

prescaleは整数でなければならないので，`round`で四捨五入する．

### PWMパルスのオンとオフのタイミングを指定する

多くの場合，
設定したい[パルス幅[s],角度]の情報をもとに，パルス幅[s]をステップ<4096に変換して，PCA9685に送る．
パルス幅$`\Delta t`$をステップ数に変換するには，

#### MG996R

| パルス幅 (s) | 角度 |
|---|---|
| 1.0 ms | 0° |
| 1.5 ms | 90° |
| 2.0 ms | 180° |

#### DS3218

| パルス幅 (s) | 角度 |
|---|---|
| 0.5 ms | 0° |
| 1.5 ms | 90° |
| 2.5 ms | 180° |

#### HS-5086WP

| パルス幅 (s) | 角度 |
|---|---|
| 0.9 ms | 0° |
| 1.5 ms | 90° |
| 2.1 ms | 180° |

$`4096 * \Delta t / T_{\rm PWM}`$を計算すればよい．

'''


try:
    # microptyhonの場合
    from machine import SoftI2C as I2C, Pin
    import ustruct as struct
    import utime as time
    import math
    _MicroPython_ = True
except:
    # ラズパイの場合
    try:
        _MicroPython_ = False
        import smbus
        from time import sleep
        import time
        import math

    except:
        print("\u001b[35m")
        print('please install smbus')
        print("\u001b[0m")

from ..libi2c import *

#@ -------------------------------------------------------- #
#@                          PCA9685                         #
#@ -------------------------------------------------------- #
# @ Adafruitのライブラリをmicropythonとラズパイの両方で使えるように修正した

# Registers/etc:
PCA9685_ADDRESS = 0x40
MODE1 = 0x00
MODE2 = 0x01
SUBADR1 = 0x02
SUBADR2 = 0x03
SUBADR3 = 0x04
PRESCALE = 0xFE
LED0_ON_L = 0x06
LED0_ON_H = 0x07
LED0_OFF_L = 0x08
LED0_OFF_H = 0x09
ALL_LED_ON_L = 0xFA
ALL_LED_ON_H = 0xFB
ALL_LED_OFF_L = 0xFC
ALL_LED_OFF_H = 0xFD

# Bits:
RESTART = 0x80
SLEEP = 0x10
ALLCALL = 0x01
INVRT = 0x10
OUTDRV = 0x04 


class PCA9685:
    """PCA9685 PWM LED/servo controller."""

    def __init__(self, address=PCA9685_ADDRESS, i2c=None):
        self.address = address
        """Initialize the PCA9685."""
        # Setup I2C interface for the device.
        if _MicroPython_:
            if i2c:
                self.bus = i2c
            else:
                self.bus = I2C(scl=Pin(22), sda=Pin(21))
                print('self.bus.scan()  ', self.bus.scan())
        else:
            self.bus = smbus.SMBus(1)

        self.set_all_pwm(0, 0)
        write_byte_data(self.bus, self.address, MODE2, OUTDRV)
        write_byte_data(self.bus, self.address, MODE1, ALLCALL)
        time.sleep(0.005)  # wait for oscillator
        mode1, = read_byte_data(self.bus, self.address, MODE1, 1)
        mode1 = mode1 & 0xFF
        mode1 = mode1 & ~SLEEP  # wake up (reset sleep)
        write_byte_data(self.bus, self.address, MODE1, mode1)
        time.sleep(0.005)  # wait for oscillator


    def set_pwm_freq(self, freq_hz):
        """Set the PWM frequency to the provided value in hertz."""        
        oldmode = read_byte_data(self.bus, self.address, MODE1, 1)[0]  # リストの最初の要素を取得
        oldmode = oldmode & 0xFF
        newmode = (oldmode & 0x7F) | 0x10  # sleep
        write_byte_data(self.bus, self.address, MODE1, newmode)  # go to sleep
        prescale_value = round(25000000.0 / (4096.0 * float(freq_hz))) - 1
        write_byte_data(self.bus, self.address, PRESCALE, prescale_value)
        write_byte_data(self.bus, self.address, MODE1, oldmode)
        time.sleep(0.005)
        write_byte_data(self.bus, self.address, MODE1, oldmode | 0x80)


    def set_pwm_offonly(self, channel, off):
        """Sets a single PWM channel."""
        write_byte_data(self.bus, self.address, LED0_ON_L+4*channel, on & 0xFF)
        write_byte_data(self.bus, self.address, LED0_ON_H+4*channel, on >> 8)
        write_byte_data(self.bus, self.address, LED0_OFF_L+4*channel, off & 0xFF)
        write_byte_data(self.bus, self.address, LED0_OFF_H+4*channel, off >> 8)

    def set_pwm(self, channel, on, off):
        """Sets a single PWM channel."""
        write_byte_data(self.bus, self.address, LED0_ON_L+4*channel, on & 0xFF)
        write_byte_data(self.bus, self.address, LED0_ON_H+4*channel, on >> 8)
        write_byte_data(self.bus, self.address, LED0_OFF_L+4*channel, off & 0xFF)
        write_byte_data(self.bus, self.address, LED0_OFF_H+4*channel, off >> 8)

    def set_all_pwm(self, on, off):
        """Sets all PWM channels."""
        write_byte_data(self.bus, self.address, ALL_LED_ON_L, on & 0xFF)
        write_byte_data(self.bus, self.address, ALL_LED_ON_H, on >> 8)
        write_byte_data(self.bus, self.address, ALL_LED_OFF_L, off & 0xFF)
        write_byte_data(self.bus, self.address, ALL_LED_OFF_H, off >> 8)
