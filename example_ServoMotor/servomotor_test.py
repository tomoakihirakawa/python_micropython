from lib.servomotor import *
from lib.PCA9685 import *
import time

pwm = PCA9685(0x40)
pwm.set_pwm_freq(50)

servos = [MG996R(0,pwm), MG996R(1,pwm), MG996R(2,pwm)]

# for s in servos:
#     s.setDegree(0)
# time.sleep(100)

for x in range(0,190,30):
    servos[0].setDegree(x)
    for y in range(0,190,30):
        servos[1].setDegree(y)        
        for z in range(0,190,30):
            servos[2].setDegree(z)
            print(x,y,z)
            time.sleep(0.1)