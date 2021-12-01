
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
m = MediatorUDP(remote="192.168.1.40")
m({"set": {"period": 0.01}})
# -------------------------------------------------------- #

#b% -------------------------------------------------------- #
#b%                        fusionの作成                       #
#b% -------------------------------------------------------- #

T_ns_ = 0
T_ns = 0

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
                a = 0.1
                A[i] = (1-a)*A[i] + a*m.get("accel")[i]
                M[i] = (1-a)*M[i] + a*m.get("mag")[i]
                G[i] = (1-a)*G[i] + a*m.get("gyro")[i]
                count = count + 1
        print("A=", A, ",M=", M, "G=", G)
    except:
        m({"set": {"period": 0.01}})
        sleep(1.)
        pass

    if count > 500:
        break

fusion = Fusion(Times(6, A), M)  # %fusion作成

#b% -------------------------------------------------------- #

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
minmax_mag = [[-1.697467, 5.971639],
              [-2.728203, 4.904211],
              [-2.400453, 4.977203]]
bias_mag = (minmax_mag[0][1]-minmax_mag[0][0],
            minmax_mag[1][1]-minmax_mag[1][0],
            minmax_mag[2][1]-minmax_mag[2][0])
#b@ ----------------------------------------------------------------- #
current_time_ = 0.
current_time = 0.
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
            accel = Times(6, data["accel"])
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
