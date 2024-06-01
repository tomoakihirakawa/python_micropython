'''DOC_EXTRACT 0_2_servomotor

## ライトヒルのロボットの制御

ライトヒルの曲線に，ロボットの節が乗るようにするためのサーボモーターの角度の計算方法は他の場所で説明している．
ここでは，実査によって得られた角度を各モーターに与えてみる．
やることは，複数のサーボモーターの制御と同じ．

![sample_lighthill.gif](sample_lighthill.gif)

'''

import threading


import math
from lib.servomotor import *
from time import sleep, time_ns

# 電力計のためのライブラリ
from ina226 import INA226

# ロードセルのためのライブラリ
import sys
import RPi.GPIO as GPIO
from hx711 import HX711

P = 0.0
V = 0.0
I = 0.0
F = 0.0
a = 0.7

def read_ina226():
    global P, V, I
    while not exit_flag:  # Use an exit flag to control the thread's loop
        if ina.is_conversion_ready():
            P = a * P + (1-a) * ina.power()
            V = a * V + (1-a) * ina.voltage()
            I = a * I + (1-a) * ina.current()
            sleep(0.3)

def read_hx711():
    global F
    while not exit_flag:
        # F = a * F + (1-a) * hx.get_weight(5)
        F = hx.get_weight(3)
        sleep(0.1)

# ---------------------------------------------------------------------------- #
# 電力計のための初期化
print("===================================================Begin to read")
ina = INA226(address=0x43, shunt_ohms=0.002, max_expected_amps=25)
print("===================================================Begin to configure")
ina.configure()
print("===================================================Begin to set low battery")
ina.wake()
print("===================================================Begin to read")
# ---------------------------------------------------------------------------- #
# ロードセルのための初期化
PIN_DAT = 5
PIN_CLK = 6
referenceUnit = 1 # <=これを決めたい
def cleanAndExit():
    print("Cleaning...")
    GPIO.cleanup()
    print("Bye!")
    sys.exit()
hx = HX711(PIN_DAT, PIN_CLK)
# データの並び順を指定
hx.set_reading_format("MSB", "MSB")
# キャリブレーション値を設定
hx.set_reference_unit(referenceUnit)
hx.reset()
hx.tare()
print("Tare done! Add weight now...")
# ---------------------------------------------------------------------------- #
# Assuming LighthillRobot as LHR
import LighthillRobot as LHR

# Initialize the LighthillRobot
L = 0.3
period = 0.2
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

exit_flag = False  # Flag to control thread termination

ina_thread = threading.Thread(target=read_ina226)
hx_thread = threading.Thread(target=read_hx711)
ina_thread.start()
hx_thread.start()

to_degree = 180 / math.pi

start_time = time_ns() # Start time in nanoseconds
last_print_time = time_ns() - start_time  # Last time printed in nanoseconds
last_calculated_time = time_ns() - start_time # Last time calculated in nanoseconds

try:
    while True:
        current_time = time_ns() - start_time # Current time in nanoseconds
        for i, angle in enumerate(robot.getAngles(current_time * 1e-9)):
            s[i].setDegree(90 + angle * to_degree)

        if (current_time - last_print_time) >= 0.1 * 1e+9:  # Print every 0.1 seconds
            print(f"Power: {P:.3f} mW, Voltage: {V:.3f} V, Current: {I:.3f} mA, Force: {F:.3f} g")
            last_print_time = current_time

        sleep(0.05)  # Adjust delay as needed for your servomotor update rate

except KeyboardInterrupt:
    exit_flag = True  # Signal threads to exit
    cleanAndExit()  # Clean up resources