'''DOC_EXTRACT PCA9685

## PCA9685

* PWMの周波数を生成するようPCA9685を設定する方法
* デューティーサイクルを決める，PWMパルスのオンとオフのタイミングを指定する方法

### 50Hzを作る

PCA9685の内部クロック周波数は25MHz．
PWM周期$`T_{\rm PWM}`$の中に4096個のステップが入るようにprescaleを設定する．
いいかえると，1秒間に$`4096/T_{\rm PWM}=4096 f_{\rm PWM}`$回のステップがはいるようにPCA9685のクロックを設定する．
これには，以下の式を満たすようにprescaleを設定すればよいことがわかる．

```math
\begin{align*}
4096 f_{\rm PWM} &= 25M / (prescale+1)\\
\rightarrow prescale &= \frac{25M}{4096 f_{\rm PWM}} - 1
\end{align*}
```

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
        oldmode = read_byte_data(self.bus, self.address, MODE1, 1)
        oldmode = oldmode & 0xFF
        newmode = (oldmode & 0x7F) | 0x10    # sleep
        write_byte_data(self.bus, self.address, MODE1, newmode)  # go to sleep
        write_byte_data(self.bus, self.address, PRESCALE, round(25000000.0 / (4096.0 * float(freq_hz))) - 1.)
        write_byte_data(self.bus, self.address, MODE1, oldmode)
        time.sleep(0.005)
        write_byte_data(self.bus, self.address, MODE1, oldmode | 0x80)

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

# -------------------------------------------------------- #


def example():

    def Subdivide(min, max, num):
        return [min+i*(max-min)/(num-1) for i in range(num)]

    class servomotor:
        """
        MG996Rの場合，
        0.4ms
        """

        min_len_deg = [0.0005, 0]
        max_len_deg = [0.0025, 180]

        def __init__(self, ch_IN, offset_IN=0):
            self.ch = ch_IN
            self.offset = offset_IN
            self.pwm = PCA9685(address=0x40)
            self.freq = 50.
            self.pwm.set_pwm_freq(50.)


            # 0.5ms * 50Hz * 4096 bit = 1024 pulse            
            self.min_pulse = 4096. * self.min_len_deg[0] * self.freq
            # 2.5ms * 50Hz * 4096 bit = 5120 pulse
            self.max_pulse = 4096. * self.max_len_deg[0] * self.freq
            self.pulse_range = 4096. * (self.max_len_deg[0] - self.min_len_deg[0]) * self.freq

        # def setPWM(self, p):
        #     self.pwm.set_pwm(self.ch, 0, int((650.-150.)*p/180.+150+self.offset))

        def setDegree(self, deg):
            #!roundを使うべき

            a = (deg/180.)
            pulse = round(4096. * self.freq * (a * self.max_len_deg[0] + (1. - a) * self.min_len_deg[0]))
            self.pwm.set_pwm(self.ch, 0, pulse)

        def setDegreeByTime(self, min, max, elapsedtime, step=300):
            start = time.time()
            angles = Subdivide(min, max, step)
            times = Subdivide(0, elapsedtime, step)  # sec
            for a, t in zip(angles, times):
                while True:
                    if time.time() - start >= t:
                        self.setDegree(a)
                        break

        def setPWM(self, pwm):
            self.pwm.set_pwm(self.ch, 0, round(pwm))

        def clean(self):
            self.setPWM(90)
            time.sleep(1)

    # -------------------------------------------------------- #

    s = servomotor(0, 0)
    min = 0
    max = 180

    s.setDegree(min)
    time.sleep(1)

    if _MicroPython_:
        start = time.time_ns()
    else:
        start = time.time()

    angles = Subdivide(min, max, 1000)
    times = Subdivide(0, 10, 1000)  # sec
    for a, t in zip(angles, times):
        while True:
            if _MicroPython_:
                dt = (time.time_ns() - start) * 10**-9
            else:
                dt = time.time() - start
            if dt >= t:
                print(a)
                s.setDegree(a)
                break


if __name__ == '__main__':
    example()
