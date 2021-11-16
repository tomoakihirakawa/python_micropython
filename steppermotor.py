from time import sleep, sleep_ms, sleep_us, time, time_ns
from machine import Pin
import _thread
import math
import machine
machine.freq(240000000)


class StepperMotor():

    def __init__(self, **kwargs):
        self.FREQ = kwargs.get('freq', 0)
        self.Pin_dir = Pin(kwargs.get('dir', 12), Pin.OUT)
        self.Pin_step = Pin(kwargs.get('step', 13), Pin.OUT)

        self.PWM_step = machine.PWM(self.Pin_step)
        self.PWM_step.freq(self.FREQ)
        self.PWM_step.duty(512)
        # ---------
        self.DIR = 1
        self.dir(self.DIR)
        # ---------
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
        print(w)
        self.freq(self.FREQ + w)


motor = StepperMotor(dir=12, step=13)

motor.start()

start = time_ns()

'''
どのモードでも，およそ７回転/秒が最大速度．
その半分の速度の場合，かなり安定して動かすことができると思われるので，基本の回転速度を最大速度の約半分に設定する．


|     |      |       max freq 12V      |                                              |
|=====================================================================================|
|  1  |  200 |  ~  1500 (Hz)=(step/s)  | ~  1500(step/s)/200(step/rot)  = 7.5(rot/s)  |
|  4  |  800 |  ~  6000 (Hz)=(step/s)  | ~  6000(step/s)/800(step/rot)  = 7.5(rot/s)  |
|  8  | 1600 |  ~ 12000 (Hz)=(step/s)  | ~ 12000(step/s)/1600(step/rot) = 7.5(rot/s)  |
| 16  | 3200 |  ~ 24000 (Hz)=(step/s)  | ~ 24000(step/s)/1600(step/rot) = 7.5(rot/s)  |
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

# -------------------------------------------------------- #
#                     一定の回転速度変化                      #
# -------------------------------------------------------- #

step_rot_1 = 200  # (step/rot)
step_rot_4 = 800  # (step/rot)
step_rot_8 = 1600  # (step/rot)
step_rot_16 = 3200  # (step/rot)


def sinOmega1():
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
    global motor
    s = time_ns()
    T = 2.*math.pi  # period
    A = 3.*1600.  # amplitude
    while True:
        # sleep(0.001)
        t = (time_ns()-s)*10**-9
        tmp = round(A*math.sin(2.*math.pi*t/T))
        print(tmp)
        motor.freq(tmp)


thread_process_loop = _thread.start_new_thread(sinOmega1, ())

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
