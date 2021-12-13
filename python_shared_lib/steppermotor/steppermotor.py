try:
    import utime as time
    from time import sleep, sleep_ms, sleep_us, time, time_ns
    from machine import Pin
    import _thread
    import math
    import machine
except:
    import time


'''
どのモードでも，およそ７回転/秒が最大速度．
その半分の速度の場合，かなり安定して動かすことができると思われるので，基本の回転速度を最大速度の約半分に設定する．

|     |      | max freq for 12V      |                                             |
| --- | ---- | --------------------- | ------------------------------------------- |
| 1   | 200  | ~  1500 (Hz)=(step/s) | ~  1500(step/s)/200(step/rot)  = 7.5(rot/s) |
| 4   | 800  | ~  6000 (Hz)=(step/s) | ~  6000(step/s)/800(step/rot)  = 7.5(rot/s) |
| 8   | 1600 | ~ 12000 (Hz)=(step/s) | ~ 12000(step/s)/1600(step/rot) = 7.5(rot/s) |
| 16  | 3200 | ~ 24000 (Hz)=(step/s) | ~ 24000(step/s)/1600(step/rot) = 7.5(rot/s) |
'''

'''
1600(step/rot)の場合，
W(Hz=step/s)/1600(step/rot) = W/1600 (rot/s)
一回転で進む距離，c(m/rot)=0.04(m/rot)?
---------------------------------------
   V = c *    W / 1600  (m/s)
dVdt = c * dWdt / 1600  (m/s^2)
---------------------------------------
'''


class steppermotor():

    def __init__(self, **kwargs):
        self.FREQ = kwargs.get('freq', 0)
        self.Pin_dir = Pin(kwargs.get('dir', 12), Pin.OUT)
        self.Pin_step = Pin(kwargs.get('step', 13), Pin.OUT)

        self.PWM_step = machine.PWM(self.Pin_step)
        self.PWM_step.freq(self.FREQ)
        self.PWM_step.duty(512)
        # ---------------------
        self.DIR = 1
        self.dir(self.DIR)
        # ---------------------
        self.asymptotic_loop = None
        self.wave_loop = None
        # ---------------------
        print("freq ", self.FREQ)
        print("Pin_dir ", self.Pin_dir)
        print("Pin_step ", self.Pin_step)
        print("PWM_step ", self.PWM_step)

    def start(self):
        sleep_us(500)

    def dir(self, dir_IN=None):
        if dir_IN is None:
            return self.DIR
        if self.Pin_dir.value() is not dir_IN:
            self.DIR = dir_IN
            self.Pin_dir.value(dir_IN)
        return self.DIR

    # 2021/11/06
    # このクラスのfreqはマイナスの値を許容し，マイナスの場合は逆回転する．
    def freq(self, freq_IN=None):
        if freq_IN is None:
            # pwmの仕様を真似するために，freq()で値が返るようにした．
            return self.FREQ
        else:
            # freq()に値が与えられた場合は設定される
            self.FREQ = freq_IN
            if self.FREQ < 0:
                self.dir(0)
                self.PWM_step.freq(-self.FREQ)
            else:
                self.dir(1)
                self.PWM_step.freq(self.FREQ)
        return self.FREQ

    def accel(self, w):
        self.freq(self.FREQ + w)

    # -------------------------------------------------------- #

    # このループはthread用
    def asymptotic(self, base_freq):
        while True:
            sleep(0.1)
            self.freq(round(self.FREQ+(base_freq - self.FREQ)/10))
        # 例えばself.freq=0でbase_freq=1000の場合．10

    def exit_asymptotic(self):
        try:
            self.asymptotic_loop.exit()
        except:
            pass

    def start_asymptotic(self, base_freq):
        self.exit_asymptotic()
        self.asymptotic_loop = _thread.start_new_thread(
            self.asymptotic, (base_freq,))

    # -------------------------------------------------------- #

    def sin_wave(self, AT_timelimit):
        '''
        この関数は周波数freq(Hz)であり，freq(step/秒)でもある．
        マイクロステップ8を使った場合，1600(step/1回転)なので，1600で割ることで，W = freq/1600 (回転/秒)になる．
        --------------------------------------------------------
        W = A*math.sin(2.*pi*t/T)
        dWdt = 2.*pi/T * A*math.cos(2.*pi*t/T)

        もし周期TをT=2πとして，A=1600とすれば，

        W = 1600*math.sin(t)
        dWdt = 1600*math.cos(t)

        V = c*math.sin(t)
        dVdt = c*math.cos(t)

        となり，速度と加速度の振幅は一致する．
        '''
        s = time_ns()
        t = s
        # T = 2.*math.pi  # period
        # A = 3.*1600.  # amplitude
        A = 0
        T = 0
        timelimit = 30
        if len(AT_timelimit) == 3:
            A, T, timelimit = AT_timelimit
        elif len(AT_timelimit) == 2:
            A, T = AT_timelimit
        else:
            return
        w = 2.*math.pi/T
        while True:
            t = (time_ns()-s)*10**-9
            if t >= timelimit:
                break
            else:
                self.freq(round(A*math.sin(w*t)))
        self.freq(0)
        
    def cos_wave(self, AT_timelimit):
        s = time_ns()
        t = s
        A = 0
        T = 0
        timelimit = 30
        if len(AT_timelimit) == 3:
            A, T, timelimit = AT_timelimit
        elif len(AT_timelimit) == 2:
            A, T = AT_timelimit
        else:
            return
        w = 2.*math.pi/T
        while True:
            t = (time_ns()-s)*10**-9
            if t > timelimit:
                break
            else:
                self.freq(round(A*math.cos(w*t)))
        self.freq(0)        
        
    def exit_wave(self):
        try:
            self.wave_loop.exit()
        except:
            pass

    def start_sin_wave(self, AT):
        self.exit_wave()
        self.wave_loop = _thread.start_new_thread(
            self.sin_wave, (AT,))

    def start_cos_wave(self, AT):
        self.exit_wave()
        self.wave_loop = _thread.start_new_thread(
            self.cos_wave, (AT,))

    def start_sin_wave_limited_time(self, AT):
        self.exit_wave()
        self.wave_loop = _thread.start_new_thread(
            self.sin_wave, (AT,))

    def start_cos_wave_limited_time(self, AT):
        self.exit_wave()
        self.wave_loop = _thread.start_new_thread(
            self.cos_wave, (AT,))
    # -------------------------------------------------------- #

##! -------------------------------------------------------- #
##! -------------------------------------------------------- #
##! -------------------------------------------------------- #


if __name__ == '__main__':

    motor = steppermotor(dir=12, step=13)
    motor.start()
    motor.start_sin_wave((1600, 1))
    sleep(100)
    # motor.start_asymptotic(5000)
    # for i in range(100):
    #     sleep(2)
    #     motor.accel(5000)
    #     sleep(2)
    #     motor.accel(-5000)
    # -------------------------------------------------------- #
    #                     一定の回転速度変化                      #
    # -------------------------------------------------------- #
    # start = time_ns()

    # step_rot_1 = 200  # (step/rot)
    # step_rot_4 = 800  # (step/rot)
    # step_rot_8 = 1600  # (step/rot)
    # step_rot_16 = 3200  # (step/rot)

    # def sinOmega1():
    #     '''
    #     この関数は周波数freq(Hz)であり，freq(step/秒)でもある．
    #     マイクロステップ8を使った場合，1600(step/1回転)なので，1600で割ることで，W = freq/1600 (回転/秒)になる．
    #     --------------------------------------------------------
    #     W = A*math.sin(2.*pi*t/T)
    #     dWdt = 2.*pi/T * A*math.cos(2.*pi*t/T)

    #     もし周期TをT=2πとして，A=1600とすれば，

    #     W = 1600*math.sin(t)
    #     dWdt = 1600*math.cos(t)

    #     V = c*math.sin(t)
    #     dVdt = c*math.cos(t)

    #     となり，速度と加速度の振幅は一致する．
    #     '''
    #     global motor
    #     s = time_ns()
    #     T = 2.*math.pi  # period
    #     A = 3.*1600.  # amplitude
    #     while True:
    #         # sleep(0.001)
    #         t = (time_ns()-s)*10**-9
    #         tmp = round(A*math.sin(2.*math.pi*t/T))
    #         print(tmp)
    #         motor.freq(tmp)

    # thread_process_loop = _thread.start_new_thread(sinOmega1, ())

    # -------------------------------------------------------- #
    #                  マイクロステップ8の場合                     #
    # -------------------------------------------------------- #
    # base_freq = round(1000)

    # def updateSpeed():
    #     global motor
    #     start = time()
    #     dfreq = base_freq - motor.freq()
    #     while True:
    #         dfreq = base_freq - motor.freq()
    #         sleep(0.001)
    #         motor.freq(round(motor.freq()+dfreq/1000))

    # while True:
    #     for i in range(5):
    #         sleep(0.05)
    #         t = (time_ns() - start)*10**-9
    #         # tmp = round(2500.*math.sin(t*2*3.14/2.)+8000.)
    #         # print(t, ", ", tmp, ", ", motor.freq())
    #         print(t, ", ", motor.freq())
    #         motor.freq(motor.freq()+1000)
    #     for i in range(2):
    #         sleep(0.05)
    #         t = (time_ns() - start)*10**-9
    #         # tmp = round(2500.*math.sin(t*2*3.14/2.)+8000.)
    #         # print(t, ", ", tmp, ", ", motor.freq())
    #         print(t, ", ", motor.freq())
    #         motor.freq(motor.freq()-1000)
