
import matplotlib.pyplot as plt
from openNetwork import *
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
m = MediatorUDP(remote="10.0.1.5")
m({"set": {"period": 0.02}})
m({"setLowPass": 0.5})
# -------------------------------------------------------- #

# t_ns = 0
# t_ns_last = 0
# data = []
# count = 0
# while True:
#     sleep(0.03)
#     try:
#         t_ns = m.get("time_ns")
#         if t_ns and t_ns is not t_ns_last:
#             print(count)
#             t_ns_last = t_ns
#             data.append(m().copy())
#             count = count + 1
#     except:
#         pass
#     if count > 1000:
#         break

# f = open("./dataAHRS.json", "w")
# json.dump(data, f, ensure_ascii=True)
# f.close()

# -------------------------------------------------------- #
fusion = None
gravity = (0, 0, 0)
gravity_norm = 0.
mean_mag = []
mean_gravity = []
gyros = []
# while True:
#     m({"set": {"period": 0.02}})
#     sleep(0.1)
#     try:
#         print(m()["accel"], Norm(m()["accel"]))
#     except:
#         pass

# m({"setOffset": (-0.24, -0.44, 2.766)})
# m({"setScale": (0.972, 1.038, 0.9868)})
T_ns_ = 0
T_ns = 0
sleep(2.)

mag_lowpass = [0, 0, 0]
mag_minmax = [[100, -100], [100, -100], [100, -100]]
mag_bias = [0, 0, 0]
while True:
    sleep(0.02)
    data = m()
    # print(m())
    try:
        T_ns_ = T_ns
        T_ns = data.get("time_ns")
        if T_ns_ is not T_ns:
            gravity = Times(5, data["accel"])
            # print(Normalize(data.get("mag")))
            mag = data["mag"]
            mean_mag.append(mag)
            mean_gravity.append(gravity)
            gyros.append(data["gyro"])
            for i in range(3):
                if mag_minmax[i][1] < mag[i]:
                    mag_minmax[i][1] = mag[i]
                if mag_minmax[i][0] > mag[i]:
                    mag_minmax[i][0] = mag[i]
                mag_bias[i] = (mag_minmax[i][0]+mag_minmax[i][1])/2.

            mag_lowpass[0] = mag_lowpass[0]*0.9 + 0.1*mag[0] - mag_bias[0]
            mag_lowpass[1] = mag_lowpass[1]*0.9 + 0.1*mag[1] - mag_bias[1]
            mag_lowpass[2] = mag_lowpass[2]*0.9 + 0.1*mag[2] - mag_bias[2]
            print(" mag_lowpass", Norm(mag_lowpass),
                  " mag_bias", mag_bias,
                  " mag_minmax = ", mag_minmax)
        # 重力や磁場の情報から姿勢を計算するfusionクラス
    except:
        m({"set": {"period": 0.01}})
        sleep(1.)
        pass
    if len(mean_mag) > 100:
        fusion = Fusion(mean_gravity[0], mean_mag[0])
        gravity_norm = Norm(Mean(mean_gravity))
    if fusion:
        break
mean_gyro = Mean(gyros)

print("gravity:", gravity)
print("    mag:", mag)
print("mean_gyro):", mean_gyro)
print(" mag_bias", mag_bias)
start = time_ns()
# sleep(100.)
# -------------------------------------------------------- #

# 1.8617249999999999, 1.0916135, 0.4112244999999999
# 1.824341, 1.121521, 0.6878659999999999

# mag_bias = [2.2245404499999997, 1.057661, 0.55914]
# mag_minmax = [[-0.4792341, 4.928315],
#               [-2.139901, 4.255223], [-2.414524, 3.532804]]

fusion.setOffsetM([1.7629009999999998, 1.05761, 0.601796])

# sleep(1.)


# def calibrate_visually(time_span):
#     start = time_ns()
#     # ------------------------- 図 ------------------------- #
#     fig = plt.figure()  # 図を生成
#     ax3d = fig.add_subplot(111, projection='3d')  # fig内部に軸を生成
#     r = [-3., 3.]  # range
#     ax3d.set_xlim(r)
#     ax3d.set_ylim(r)
#     ax3d.set_zlim(r)
#     sc = ax3d.scatter([0.], [0.], [0.])

#     data = [[], [], []]
#     while True:
#         accel = m.get("accel")
#         mag = m.get("mag")
#         gyro = m.get("gyro")
#         current_time = (time_ns()-start)*10**-9

#         # -------------------------------------------------------- #
#         for i in range(3):
#             if mag_minmax[i][1] < mag[i]:
#                 mag_minmax[i][1] = mag[i]
#             if mag_minmax[i][0] > mag[i]:
#                 mag_minmax[i][0] = mag[i]
#             mag_bias[i] = (mag_minmax[i][0]+mag_minmax[i][1])/2.
#         fusion.setOffsetM(mag_bias)
#         print(" mag_bias", mag_bias)
#         # -------------------------------------------------------- #

#         Q = fusion.solveForQuaternion(
#             accel,
#             mag,
#             gyro,
#             current_time)
#         v = fusion.interpM(current_time)  # data["mag"]
#         data[0].append(v[0])  # 図用にmagにデータを蓄積
#         data[1].append(v[1])  # 図用にmagにデータを蓄積
#         data[2].append(v[2])  # 図用にmagにデータを蓄積
#         sc._offsets3d = (data[0], data[1], data[2])
#         ax3d.relim()
#         ax3d.autoscale_view(True, True, True)
#         fig.canvas.draw()
#         fig.canvas.flush_events()
#         plt.pause(0.01)


# calibrate_visually(100.)

# -------------------------------------------------------- #
# fusion.setOffsetM((1.22, 1.32, 0.62))

# fusion.setOffsetM(mag_bias)
# fusion.setMagTransMat(((-0.037151, 0.311526, 1.08116),
#                        (0.854401, - 0.286639, 0.0104439),
#                        (0.19649, 1.00425, -0.484675)))

# fusion.setMagTransMat([(0.0197872, 0.905085, -0.117885),
#                       (0.532323, -0.253073, 1.01524),
#                       (0.875692, 0.260873, -0.740014)])

# -------------------------------------------------------- #

# print("磁場のオフセットを計算")
# X3d = []
# Y3d = []
# Z3d = []
# for i in range(1000):
#     sleep(0.02)
#     data = m()
#     try:
#         accel = data.get("accel")
#         mag = data.get("mag")
#         gyro = data.get("gyro")
#         current_time = (time_ns()-start)*10**-9
#         Q = fusion.solveForQuaternion(
#             accel,
#             mag,
#             gyro,
#             current_time)
#         v = fusion.interpM(current_time)  # data["mag"]
#         print(v)
#         X3d.append(v[0])
#         Y3d.append(v[1])
#         Z3d.append(v[2])
#         print("fusion.calculateOffsetM() = ", fusion.calculateOffsetM())
#     except:
#         print("error")
#         pass
# m({"set": {"period": 1.}})

# fig = plt.figure()  # 図を生成
# ax3d = fig.add_subplot(111, projection='3d')  # fig内部に軸を生成
# sc = ax3d.scatter(X3d, Y3d, Z3d)
# ax3d.relim()
# ax3d.autoscale_view(True, True, True)
# plt.show(block=False)
# plt.pause(10)
# -------------------------------------------------------- #


m({"setLowPass": 0.7})

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


current_time_ = 0.
current_time = 0.
accel = [0., 0., 0.]
mag = [0., 0., 0.]
T_ns = 0
for i in range(10000):
    sleep(0.005)
    try:
        data = m()
        current_time_ = current_time
        current_time = (time_ns()-start)*10**-9

        T_ns_ = T_ns
        T_ns = data.get("time_ns")
        if T_ns_ is not T_ns:
            # accel = data["accel"]
            accel = Times(5, data["accel"])
            mag = data.get("mag")
            gyro = Subtract(data.get("gyro"), mean_gyro)
            print("dt = ", current_time-current_time_)
            # -------------------------------------------------------- #
            # if i > 10 and Norm(accel) > gravity_norm*1.5:
            #     try:
            #         Q = fusion.solveForQuaternionModified(
            #             accel,
            #             mag,
            #             gyro,
            #             current_time)
            #         print(red, Q(), default)
            #     except:
            #         Q = fusion.solveForQuaternion(
            #             accel,
            #             mag,
            #             gyro,
            #             current_time)
            #         print(blue, Q(), default)
            # else:
            if i > 5:
                Yapprox0.append(fusion.interpAbody(current_time)[0])

            Q = fusion.solveForQuaternion(
                accel,
                mag,
                gyro,
                current_time)
            # print(blue, Q(), default)
            # print("fusion.calculateOffsetM() = ", fusion.calculateOffsetM())
            # print(blue, Q(), default)
            # else:
            #     accel = fusion.interpA(current_time)
            #     mag = fusion.interpM(current_time)
            #     gyro = fusion.interpW(current_time)
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
