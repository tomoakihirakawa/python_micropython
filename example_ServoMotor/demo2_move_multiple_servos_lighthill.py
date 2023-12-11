'''DOC_EXTRACT 0_2_servomotor

## ライトヒルのロボットの制御

ライトヒルの曲線に，ロボットの節が乗るようにするためのサーボモーターの角度の計算方法は他の場所で説明している．
ここでは，実査によって得られた角度を各モーターに与えてみる．
やることは，複数のサーボモーターの制御と同じ．

'''

import math
from lib.servomotor import Servomotor
from time import sleep, time_ns

# Assuming LighthillRobot as LHR
import LighthillRobot as LHR

# Initialize the LighthillRobot
L = 1.
period = 1.
w = 2.*math.pi/period
k = 2.*math.pi
c1 = 0.05
c2 = 0.05
n = 2

robot = LHR.LighthillRobot(L, w, k, c1, c2, n)

# Initialize servomotors
s = [Servomotor(0, 0), Servomotor(1, 0), Servomotor(2, 0)]

# Function to update servomotor angles based on LighthillRobot
def update_servomotors(t):
    angles = robot.getAngles(t)
    for i, angle in enumerate(angles):
        servo_angle = 90 + (angle * 180 / math.pi)
        s[i].setDegree(servo_angle)

# Main loop
start_time = time_ns()
while True:
    current_time = time_ns() - start_time
    update_servomotors(current_time)
    sleep(0.01)  # Adjust delay as needed for your servomotor update rate
