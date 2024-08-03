'''DOC_EXTRAC

# MPU9250のキャリブレーション

サーボモーターで作成した３軸回転台を使ってMPU9250のキャリブレーションを行う．



'''

from lib.PCA9685 import *
from lib.servomotor import *
import time

pwm = PCA9685(0x40)
pwm.set_pwm_freq(50)

s0 = MG996R(0, pwm)
s1 = MG996R(1, pwm)
s2 = MG996R(2, pwm)

