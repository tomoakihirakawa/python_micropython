'''DOC_EXTRACT 3_1_servomotor

## 無線ライトヒル魚ロボットの操作方法

### 事前準備

まず，無線魚ロボットと同じ準備をする．

違いは，c++で書かれたクラスをpythonから呼び出すための`LighthillRobot.cpython-311-aarch64-linux-gnu.so`ファイルを実行するpythonプログラムと同じばしょに置いておくこと．
このファイルは，pybind11によって生成されたもので，具体的な生成方法は，`cpp/builds/build_pybind11`で説明している．
元々のc++のLighthillRobotクラスは，`cpp/include/rootFinding.hpp`内で定義されている．

パラメタによっては，不自然にサーボモータが動くことがある．
これは，魚ロボの節が，LightHillの曲線に乗るためのサーボモータ角度をNewton法でうまく求められない場合である．

実際にロボットを動かさずに，サーボモータの動きをPCで確認するプログラムを準備している（`demo_runLightHillRobot1_animate_robot.py`）．
これはラズパイで実行せず，ローカルPCで実行する．matplotlibでアニメーションを見ることができる．

<img src="demo_runLightHillRobot1_animate_robot.png" width="600px">

'''

from lib.servomotor import *
from lib.PCA9685 import *
import time
import math
import LighthillRobot as LHR  # Import the LighthillRobot shared library

# Initialize PCA9685 PWM controller
pwm = PCA9685(0x40)
pwm.set_pwm_freq(50)

# Initialize two servo motors
servo = [HS5086WP(12, pwm), HS5086WP(4, pwm)]

time.sleep(0.1)
# Set initial servo positions to 0 degrees
servo[0].setDegree(0)
servo[1].setDegree(0)
time.sleep(0.1)

# ------------------- LighthillRobot Setup ------------------- #
L = 0.25
period = 1.
w = 2.*math.pi/period
k = 2.*math.pi / L
c1 = 0.01
c2 = 0.01
n = 2
# 先頭があるとして

# Create an instance of LighthillRobot for a fish of length 22 cm
robot = LHR.LighthillRobot(L, w, k, c1, c2, n)

# Record start time
start_time = time.time()

while True:
    # Calculate the elapsed time
    t = time.time() - start_time
    c = (math.tanh((t-1.)*math.pi)+1.)/2.
    # Get the angles for the two servo motors from LighthillRobot
    angles = robot.getAngles(t)
    
    # Assign the first two angles to the two servos
    theta0 = c*180./math.pi*angles[0]  # Servo 1 angle
    theta1 = c*180./math.pi*angles[1]  # Servo 2 angle
    theta2 = c*180./math.pi*angles[2]  # Servo 2 angle

    # Set the servo motors to the calculated angles
    servo[0].setDegree(theta1)
    servo[1].setDegree(theta2)
    
    # Print the angles for debugging
    # print(angles)
    
    # Delay to control the update rate
    time.sleep(0.02)  # Adjust the sleep time if needed
