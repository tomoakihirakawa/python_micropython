
try:
    import machine
    import utime as time
except:
    import time

from ..PCA9685 import PCA9685

'''DOC_EXTRACT servomotor_calss

# サーボモーターのクラス

## MG996R

6Vで11kgf-cmのトルクを持つ．
$`\pm 60^\circ`$の範囲で動作する．

PWM周期は20ms，つまり周波数は1/0.02=0.5*10^2=50Hz．

1.5msのパルス幅で中立位置，0.5msで最小角度，2.5msで最大角度．

## DS3218

6Vで20kgf-cmのトルクを持つ．
$`\pm 180^\circ`$または$`\pm 270^\circ`$の範囲で動作する．

PWM周期は2.5ms，つまり周波数は1/0.0025=0.4*10^3=400Hz．

0.5-1.5msのパルス幅で中立位置，0.5-1.0msで最小角度，0.5-2.5msで最大角度．

## HS-5086WP

6Vで2.6kgf-cmのトルクを持つ．
$`\pm 60^\circ`$の範囲で動作する．

PWM周期は20ms，つまり周波数は1/0.02=0.5*10^2=50Hz．

0.9msのパルス幅で中立位置，0.5msで最小角度，2.1msで最大角度．

'''

class MG996R:

    def __init__(self, ch_IN):

        self.ms0 = 0.5 # 0.5ms
        self.deg0 = 0.

        self.ms1 = 2.5 # 2.5ms
        self.deg1 = 180.

        self.freq = 60.
        self.pwm = PCA9685(address=0x40)
        self.pwm.set_pwm_freq(self.freq)

        self.ch = ch_IN

        self.coeff = 4096. * self.freq / 1000. # 1000はmsをsに変換するため

    def setDegree(self, deg):
        a = deg/180.
        self.pwm.set_pwm_offonly(self.ch, round(self.coeff * (a * self.ms1 +  (1. - a) * self.ms0)))

    def __del__(self):
        print(f"MG996R object on channel {self.ch} is being deleted")
        self.setDegree(0)
        time.sleep(0.5)


class DS3218:

    def __init__(self, ch_IN, mode='180'):

        self.offset = 0.5 # 0.5ms

        self.ms0 = 1. # 1ms
        self.ms1 = 1.5 # 1.5ms
        self.ms2 = 2.5 # 2.5ms

        if mode == '180':
            self.deg0 = 0.
            self.deg1 = 90.
            self.deg2 = 180.
        else:
            self.deg0 = 0.
            self.deg1 = 135.
            self.deg2 = 270.

        self.freq = 60.
        self.pwm = PCA9685(address=0x40)
        self.pwm.set_pwm_freq(self.freq)

        self.ch = ch_IN

        self.coeff = 4096. * self.freq / 1000. # 1000はmsをsに変換するため

    def setDegree(self, deg):
        if deg < 90:
            a = deg / 90.
            self.pwm.set_pwm(self.ch, 
                             round(self.coeff * self.offset), 
                             round(self.coeff * ((1. - a) * self.ms0 + a * self.ms1)))
        else:
            a = deg/90. - 1.
            self.pwm.set_pwm(self.ch, 
                             round(self.coeff * self.offset), 
                             round(self.coeff * ((1. - a) * self.ms1 + a * self.ms2)))        

    def __del__(self):
        print(f"DS3218 object on channel {self.ch} is being deleted")
        self.setDegree(0)
        time.sleep(0.5)

class HS5086WP:

    def __init__(self, ch_IN):

        self.ms0 = 0.9
        self.deg0 = 0.

        self.ms1 = 2.1
        self.deg1 = 180.

        self.freq = 60.
        self.pwm = PCA9685(address=0x40)
        self.pwm.set_pwm_freq(self.freq)

        self.ch = ch_IN

        self.coeff = 4096. * self.freq / 1000. # 1000はmsをsに変換するため

    def setDegree(self, deg):
        a = deg/180.
        self.pwm.set_pwm_offonly(self.ch, round(self.coeff * (a * self.ms1 +  (1. - a) * self.ms0)))

    def __del__(self):
        print(f"HS5086WP object on channel {self.ch} is being deleted")
        self.setDegree(0)
        time.sleep(0.5)
