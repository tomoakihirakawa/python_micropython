
import matplotlib.pyplot as plt
from python_shared_lib.openNetwork import *
from math import pi, sin
from statistics import mean
import json
from integrator import *
from fundamental import *
from time import time, sleep, time_ns
# from fusion import *
# from AHRS import *
import numpy as np
from matplotlib.gridspec import GridSpec
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import Normalize
import matplotlib
from matplotlib import pyplot as plt
matplotlib.rcParams['font.family'] = 'Times New Roman'
red = "\033[31m"
blue = "\033[34m"
default = "\033[39m"


def NormalizeTuple(mag):
    norm = Norm(mag)
    return (mag[0]/norm, mag[1]/norm, mag[2]/norm)


def NormalizeList(mag):
    norm = Norm(mag)
    return [mag[0]/norm, mag[1]/norm, mag[2]/norm]


# -------------------------------------------------------- #
m = MediatorUDP(remote="10.0.1.21")
m({"set": {"period": 0.02}})
# -------------------------------------------------------- #

#b@ -------------------------------------------------------- #
#b@                        fusionの作成                       #
#b@ -------------------------------------------------------- #

fusion = None
gravity = (0, 0, 0)
gravity_norm = 0.
gyros = []

T_ns_ = 0
T_ns = 0
sleep(2.)

mag_lowpass = [0, 0, 0]
mag_minmax = [[100, -100], [100, -100], [100, -100]]
mag_bias = [0, 0, 0]
count = 0
#
A = [0, 0, 0]
M = [0, 0, 0]
G = [0, 0, 0]

while True:
    sleep(0.02)
    try:
        T_ns = m.get("time_ns")
        if T_ns_ is not T_ns:
            T_ns_ = T_ns
            for i in range(3):
                a = 0.6
                A[i] = (1-a)*A[i] + a*m.get("accel")[i]
                M[i] = (1-a)*M[i] + a*m.get("mag")[i]
                G[i] = (1-a)*G[i] + a*m.get("gyro")[i]
                count = count + 1
        print("A=", A, ",M=", M, "G=", G)
    except:
        m({"set": {"period": 0.01}})
        sleep(1.)
        pass

    if count > 100:
        break

# -------------------------------------------------------- #
fusion = Fusion(A, M)
start = time_ns()
# -------------------------------------------------------- #
IA = integratorMultiple(3)
# -------------------------------------------------------- #
fig = plt.figure()
ax0 = fig.add_subplot(311)
X = [0]
Y0 = [0]
Yapprox0 = [0]
li0, = ax0.plot(X, Y0, '-')
liApprox0, = ax0.plot(X, Yapprox0, '-')
ax1 = fig.add_subplot(312)
Y1 = [0]
li1, = ax1.plot(X, Y1, '-')
ax2 = fig.add_subplot(313)
Y2 = [0]
li2, = ax2.plot(X, Y2, '-')

fig.canvas.draw()
plt.show(block=False)


#b@ -------------------- ジャイロセンサーの校正で確認 -------------------- #
bias_gyro = (-0.07128319964117816,
             0.12235516538683028,
             0.11174474504429761)
minmax_mag = [[-1.698909, 5.94178],
              [-2.672332, 4.888905],
              [-2.648593, 4.954339]]
bias_mag = (minmax_mag[0][1]-minmax_mag[0][0],
            minmax_mag[1][1]-minmax_mag[1][0],
            minmax_mag[2][1]-minmax_mag[2][0])
#b@ ----------------------------------------------------------------- #
current_time_ = 0.
current_time = 0.
accel = [0., 0., 0.]
mag = [0., 0., 0.]
T_ns = 0
for i in range(10000):
    sleep(0.005)
    try:
        data = m()
        T_ns = data.get("time_ns")
        if T_ns_ is not T_ns:
            T_ns_ = T_ns
            current_time = (time_ns()-start)*10**-9
            # accel = data["accel"]
            accel = Times(5, data["accel"])
            mag = Subtract(data.get("mag"), bias_mag)
            gyro = Subtract(data.get("gyro"), bias_gyro)
            print("dt = ", current_time-current_time_)
            current_time_ = current_time
            # -------------------------------------------------------- #
            Q = fusion.solveForQuaternion(
                accel,
                mag,
                gyro,
                current_time)
            if i > 5:
                # gG = Q.Rs(gravity)
                # a_ = [accel[0] - gG[0], accel[1] - gG[1], accel[2] - gG[2]]
                a_ = fusion.interpAbody(current_time)
                # print(" a_ = ", a_, ", accel = ", accel,
                #       "gravity = ", gravity, ", mag = ", mag)
                IA.add(current_time, a_)
                # a_ = IA.integral
                # -------------------------------------------------------- #
                # -------------------------------------------------------- #
                X.append(current_time)
                # Yapprox0.append(fusion.interpAbody(current_time)[0])

                Y0.append(a_[0])
                # liApprox0.set_data(X, Yapprox0)
                li0.set_data(X, Y0)
                ax0.relim()
                ax0.autoscale_view(True, True, True)
                # Y.append(IA.integral[1])
                # ------------------------------------------ #
                Y1.append(a_[1])
                li1.set_data(X, Y1)
                ax1.relim()
                ax1.autoscale_view(True, True, True)
                # -------------------------------------------------------- #
                Y2.append(a_[2])
                li2.set_data(X, Y2)
                ax2.relim()
                ax2.autoscale_view(True, True, True)
                # -------------------------------------------------------- #
                fig.canvas.draw()
                plt.pause(0.0001)

    except KeyboardInterrupt:
        plt.close('all')
        m({"set": {"period": 1.}})
        break

m({"set": {"period": 1.}})
exit()

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
