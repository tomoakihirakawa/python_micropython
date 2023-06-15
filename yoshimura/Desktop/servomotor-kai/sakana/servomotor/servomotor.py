

try:
    import machine
    import utime as time
except:
    import time

from PCA9685 import PCA9685


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
        self.freq = 60.
        self.pwm.set_pwm_freq(60.)

        self.min_pulse = self.min_len_deg[0]/((1./self.freq)/(2.**12))  # 0 deg
        self.max_pulse = self.max_len_deg[0] / \
            ((1./self.freq)/(2.**12))  # 180deg
        self.pulse_range = self.max_pulse - self.min_pulse

    # def setPWM(self, p):
    #     self.pwm.set_pwm(self.ch, 0, int((650.-150.)*p/180.+150+self.offset))

    def setDegree(self, deg):
        #!roundを使うべき
        self.pwm.set_pwm(self.ch, 0, round(self.min_pulse +
                         self.pulse_range*((deg-self.offset)/180.)))

    def setDegreeByTime(self, min, max, elapsedtime, step=300):
        start = time.time()
        angles = Subdivide(min, max, step)
        times = Subdivide(0, elapsedtime, step)  # sec
        for a, t in zip(angles, times):
            while True:
                if time.time() - start >= t:
                    self.setDegree(a)
                    break

    def moveDegree(self, tup):
        [start, stop, num, slp_time] = tup
        for deg in Subdivide(start, stop, num):
            time.sleep_ms(slp_time)
            self.setDegree(deg)

    def setPWM(self, pwm):
        self.pwm.set_pwm(self.ch, 0, round(pwm))

    def clean(self):
        self.setPWM(90)
        time.sleep(1)


def servomotor_example():
    s = servomotor(0, 0)
    min = 40
    max = 140

    s.setDegree(min)
    time.sleep(1)

    start = time.time()
    angles = Subdivide(min, max, 500)
    times = Subdivide(0, 3, 500)  # sec
    for a, t in zip(angles, times):
        while True:
            if time.time() - start >= t:
                s.setDegree(a)
                break


def servomotor_example2():
    s = [servomotor(0, 0), servomotor(1, 0), servomotor(2, 0)]
    min = 30.
    max = 130.

    s[0].setDegree(min)
    s[1].setDegree(min)
    s[2].setDegree(min)

    """
    motor is < 31 [deg/s]
    """
    time.sleep(1)
    step = 600
    angles = Subdivide(min, max, step)
    times = Subdivide(0, 2.5, step)  # sec
    dt = times[1] - times[0]
    while True:
        start = time.time()
        count = 0
        for a, t in zip(angles, times):
            while True:
                # elapsedtime = time.time() - start
                if time.time() - start >= t:
                    # count += 1
                    # print(count, t)
                    s[0].setDegree(a)
                    s[1].setDegree(a)
                    s[2].setDegree(a)
                    break
        angles.reverse()


def servomotor_example3():
    s = [servomotor(0, 0), servomotor(1, 0), servomotor(2, 0)]
    min = 30.
    max = 160.

    s[0].setDegree(min)
    s[1].setDegree(min)
    s[2].setDegree(min)
    time.sleep(1)
    s[0].setDegreeByTime(min, max, 2.)
    s[1].setDegreeByTime(min, max, 2.)
    s[2].setDegreeByTime(min, max, 2.)
    s[2].setDegreeByTime(max, min, 2.)
    s[1].setDegreeByTime(max, min, 2.)
    s[0].setDegreeByTime(max, min, 2.)


if __name__ == '__main__':
    example2()
