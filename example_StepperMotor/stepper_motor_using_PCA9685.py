'''DOC_EXTRACT stepper_motor_using_PCA9685

# PCA9685を使用してステッピングモーターを制御する

PCA9685はパルスを出力するためのデバイスで，サーボモータだけでなくステッピングモータを回転させるパルスの生成にも使える．

TB6600を使って実際に行なった．

TB6600の設定：

SW1: ON
SW2: ON
SW3: OFF
SW4: ON
SW5: OFF
SW6: ON

PCA9685がステッピングモータパルス生成に利用されない理由は，
おそらくパルスの回数をカウントするのが難しいためだろう．

'''

from lib.servomotor import *
from lib.PCA9685 import *
import time

f = 800
ch = 0

pwm = PCA9685(0x40)

try:
    pwm.set_pwm_freq(f)
    coeff = pwm.decimal * pwm.freq / 1000. # 1000はmsをsに変換するため
    pwm.set_pwm(ch, 0, 0)
    time.sleep(1)
    pwm.set_pwm_off(ch, round(coeff/f))
    time.sleep(1)
    pwm.set_pwm_off(ch, 0)
    time.sleep(0.1)

except KeyboardInterrupt:

    pwm.set_pwm_off(ch, 0)
    time.sleep(0.1)