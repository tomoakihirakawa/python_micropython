'''DOC_EXTRACT 0_2_servomotor

## ライトヒルのロボットの制御

ライトヒルの曲線に，ロボットの節が乗るようにするためのサーボモーターの角度の計算方法は他の場所で説明している．
ここでは，実査によって得られた角度を各モーターに与えてみる．
やることは，複数のサーボモーターの制御と同じ．

![sample_lighthill.gif](sample_lighthill.gif)

'''

import math
from lib.servomotor import *
from time import sleep, time_ns

# Assuming LighthillRobot as LHR
import LighthillRobot as LHR

# Initialize the LighthillRobot
L = 0.4
period = 1.
w = 1.*math.pi/period
k = 2.*math.pi/L
c1 = 0.04
c2 = 0.01
n = 2

robot = LHR.LighthillRobot(L, w, k, c1, c2, n)

# Initialize servomotors
s = [servomotor(0, 0), servomotor(1, 0), servomotor(2, 0)]

for i in range(len(s)):
    for k in range(10):
        s[i].setDegree(90)

sleep(5.)

to_degree = 180 / math.pi
# Main loop
start_time = time_ns()
while True:
    current_time = (time_ns() - start_time)*1e-9
    for i, angle in enumerate(robot.getAngles(current_time)):
        s[i].setDegree(90 + angle * to_degree)
    sleep(0.01)  # Adjust delay as needed for your servomotor update rate
