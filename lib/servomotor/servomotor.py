
try:
    import machine
    import utime as time
except:
    import time

from ..PCA9685 import PCA9685

'''DOC_EXTRACT servomotor_calss

このservomotorクラスは，`servomotor(チャンネル, オフセット角度)`で初期化する．
例えば，以下のようにすると，チャンネル0のサーボモーターを初期角度90度で初期化できる．

```
s = servomotor(0, 90)
```

角度を変更するには，`setDegree`を使う．例えば，以下のようにすると，チャンネル0のサーボモーターの角度を180度に変更できる．

```
s.setDegree(180)
```

'''


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
        self.freq = 60.
        self.pwm.set_pwm_freq(60.)

        self.min_pulse = self.min_len_deg[0]/((1./self.freq)/(2.**12))  # 0 deg
        self.max_pulse = self.max_len_deg[0] / \
            ((1./self.freq)/(2.**12))  # 180deg
        self.pulse_range = self.max_pulse - self.min_pulse

    def setDegree(self, deg):
        self.pwm.set_pwm(self.ch, 0, round(self.min_pulse +
                         self.pulse_range*((deg-self.offset)/180.)))

    def setDegreeByTime(self, min, max, elapsedtime, step=300):
        start = time.time()
        angle_step = (max - min) / (step - 1)
        time_step = elapsedtime / (step - 1)

        for i in range(step):
            while True:
                if time.time() - start >= i * time_step:
                    self.setDegree(min + i * angle_step)
                    break

    def moveDegree(self, tup):
        [start, stop, num, slp_time] = tup
        degree_step = (stop - start) / (num - 1)

        for i in range(num):
            time.sleep_ms(slp_time)
            self.setDegree(start + i * degree_step)

    def setPWM(self, pwm):
        self.pwm.set_pwm(self.ch, 0, round(pwm))

    def clean(self):
        self.setPWM(90)
        time.sleep(1)
