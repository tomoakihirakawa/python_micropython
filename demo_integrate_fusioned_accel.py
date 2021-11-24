from openNetwork import *
from math import pi, sin
from statistics import mean
from integrator import *
from fundamental import *
from time import time, sleep, time_ns
# from fusion import *
from AHRS import *
import numpy as np
from matplotlib.gridspec import GridSpec
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import Normalize
import matplotlib
from matplotlib import pyplot as plt
matplotlib.rcParams['font.family'] = 'Times New Roman'

AHRS = MPU9250()

AHRS.MPU6050.calibrate_gyro()
# AHRS.AK8963.calibrate_visually(20)
AHRS.AK8963.setOffset([-0.24, -0.44, 2.766])
AHRS.AK8963.setScale([0.972, 1.038, 0.9868])


# ------------------------- 図の設定 ------------------------- #
fig = plt.figure()  # 図を生成
ax = fig.add_subplot(111)  # fig内部に軸を生成
# minmax = [-1, 1]
minmax = [-5, 5]
ax.set_xlim([0, 10])
ax.set_ylim(minmax)
# ------------------------- 計測し表示 ------------------------ #
A = [[0], [0], [0]]
IA = [[]*3]


# -------------------------------------------------------- #
q = [1, 2, 3, 4]  # クォータニオン初期値（適当に）
theta = -54  # 磁場の角度
fusion = Fusion(AHRS.accel(), AHRS.mag())  # 重力や磁場の情報から姿勢を計算するfusionクラス

"""
ノート：
accel = (0,0,-1)
mag = (cos(-54deg),0,sin(-54deg))
センサー値がこうなる姿勢を基準にすることと同じ．
この基準からのズレを計算する．
表し方は，
* ヨーピッチロール角（オイラー角の一つ）
* クォータニオン
どちらでもいい．
"""

IA = integratorMultiple(3)
a_ = [0., 0., 0.]
start_t = time_ns()
t = time_ns()
count = 0


def stepper(L, T):
    # -------------------------------------------------------- #
    m = MediatorUDP(remote="10.0.1.5")
    # -------------------------------------------------------- #
    # T = T_IN  # 周期[sec]
    c = 0.06/(2*pi)  # [m/rad] -> 1回転で進む距離は2*pi*c
    # L = 0.1   # 変位の振幅 [m]
    # -------------------------------------------------------- #
    n = 6400  # ドライバーに書いてある1回転に必要なステップ数 [step/rotation]
    a = L*n/(2*T*c)  # f = a*sin(w*t) [Hz] の a
    # m({"freq": 1600})
    print("最大速度", c*a*2.*pi/n)
    m({"start_sin_wave": (a, T)})

disp = 0.1  # [m]
period = 1  # [s]

started = False
dt = 0.
# -------------------------------------------------------- #
while count < 50000:
    count += 1
    sleep(0.01)
    tmp_a = AHRS.accel()
    accel = (tmp_a[0], tmp_a[1], tmp_a[2])
    mag = AHRS.mag()
    gyro = AHRS.gyro()
    # -------------------------------------------------------- #
    tmp_t = t
    t = time_ns()
    dt = (t - tmp_t)*(10.**-9)
    current_time = (t - start_t)*10**-9
    if not started:
        if current_time > 1:
            started = True
            # stepper(disp, period)
    elif current_time > 10:
        break

    # Fusion.updateMadwick(accel, mag, gyro, dt)
    # Fusion.update0(accel, mag, gyro, dt)
    # Fusion.update1(accel, mag, gyro, dt)
    # Fusion.update2(accel, mag, gyro, dt)
    # Fusion.update20(accel, mag, gyro, dt)
    # ypr = Fusion.YPR()
    # print(ypr[0]/pi*180., ypr[1]/pi*180., ypr[2]/pi*180.)
    Q = fusion.solveForQuaternion(accel, mag, gyro, current_time)
    if current_time > 1:
        # --------- 計測結果 ------ #
        G = [0, 0, -1.]
        gG = Q.Rs(G)
        # print(gG, ', ', accel)
        Accel = [accel[0] - gG[0],
                 accel[1] - gG[1],
                 accel[2] - gG[2]]
        alpha = .5
        a_ = [(1-alpha)*a_[0]+alpha*Accel[0],
              (1-alpha)*a_[1]+alpha*Accel[1],
              (1-alpha)*a_[2]+alpha*Accel[2]]
        IA.add(current_time, a_)

plt.plot(IA.t, IA.values, label="accel")
plt.plot(IA.t, IA.integrals, label="integral")
plt.plot(IA.t, IA.double_integrals, label="double integral")

# -------------------------------------------------------- #

# T_ = []
# SIN_ = []
# for i in range(1000):
#     t = i/100.
#     w = 2.*pi/period
#     T_.append(t)
#     SIN_.append(disp*cos(w*t-1))

# plt.plot(T_, SIN_)

# -------------------------------------------------------- #

plt.xlabel('$s(t)$', fontsize=14)
plt.ylabel('$a(m/s^2$)', fontsize=14)
plt.legend()
plt.show()
