
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

# -------------------------------------------------------- #
m = MediatorUDP(remote="10.0.1.7")
for i in range(5):
    sleep(0.5)
    m({"set": {"period": 0.001}})

#@ -------------------------------------------------------- #
#@                   ジャイロセンサーの校正で確認                #
#@ -------------------------------------------------------- #

bias_gyro = (-0.3603053, -0.09160305, -0.0610687)

# minmax_mag = [[-0.225141, 5.31778], [-0.982585, 4.41378], [-1.27578, 4.21689]]
minmax_mag = [[-4.019531, 0.8254395], [-0.873291, 3.756348], [-0.107666, 5.455078]]

bias_mag = ((minmax_mag[0][1]+minmax_mag[0][0])/2,
            (minmax_mag[1][1]+minmax_mag[1][0])/2,
            (minmax_mag[2][1]+minmax_mag[2][0])/2)

#b% -------------------------------------------------------- #
#b%                        fusionの作成                       #
#b% -------------------------------------------------------- #

T_ns_ = 0
T_ns = 0

count = 0

A = [0, 0, 0]
M = [0, 0, 0]
G = [0, 0, 0]

while True:
    sleep(0.01)
    try:
        T_ns = m.get("time_ns")
        if T_ns_ is not T_ns:
            T_ns_ = T_ns
            mag = Subtract(m.get("mag"), bias_mag)
            gravity = Times(2, m.get("accel"))
            for i in range(3):
                a = 0.2
                A[i] = (1-a)*A[i] + a*gravity[i]
                M[i] = (1-a)*M[i] + a*mag[i]
                G[i] = (1-a)*G[i] + a*m.get("gyro")[i]
                count = count + 1
        print("A=", A, ",M=", M, "G=", G)
    except:
        m({"set": {"period": 0.01}})
        sleep(1.)
        pass

    if count > 500:
        break

fusion = Fusion(A, M)  # %fusion作成
m({"set": {"period": 0.}})

#b% -------------------------------------------------------- #

start = time_ns()
IA = integratorMultiple(3)

#* -------------------------------------------------------- #
#*                           図の設定                        #
#* -------------------------------------------------------- #
fig = plt.figure()
ax = fig.add_subplot(111)
X = []
Y0 = []
Y1 = []
Y2 = []
lines = [ax.plot(X, Y0, '.-', label="x")[0],
         ax.plot(X, Y1, '.-', label="y")[0],
         ax.plot(X, Y2, '.-', label="z")[0]]
ax.set_xlabel('time (s)')
ax.set_ylabel('sensor value')
fig.canvas.draw()
plt.legend()
plt.show(block=False)

current_time_ = 0.
current_time = 0.
T_ns = 0
Q = None
accel = None
gyro = None
mag = None
m({"setLowPass": 0.8})
for i in range(10):
    sleep(0.1)
    m({"set": {"period": 0.005}})
    
m({"set": {"period": 0.005}})
for i in range(1000000):
    sleep(0.005)
    try:
        data = m()
        T_ns = data.get("time_ns")
        if T_ns_ is not T_ns:
            T_ns_ = T_ns
            current_time = (T_ns-start)*10**-9
            # accel = data["accel"]
            accel = Times(2, data["accel"])
            mag = Subtract(data.get("mag"), bias_mag)
            gyro = Subtract(data.get("gyro"), bias_gyro)
            print("dt = ", current_time-current_time_)
            current_time_ = current_time
            # -------------------------------------------------------- #
            Q = fusion.updateStandard(
                accel,
                mag,
                gyro,
                current_time,
                1.)
            if i > 5:
                # gG = Q.Rs(gravity)
                # a_ = [accel[0] - gG[0], accel[1] - gG[1], accel[2] - gG[2]]
                a_ = fusion.interpAbody(current_time)
                # a_ = fusion.interpA(current_time)
                # print(Q.Rs(A))
                # a_ = fusion.interpYPR(current_time)
                IA.add(current_time, a_)
                a_ = IA.integral
                # -------------------------------------------------------- #
                X.append(current_time)
                Y0.append(a_[0])
                Y1.append(a_[1])
                Y2.append(a_[2])
                # -------------------------------------------------------- #
                if len(X) > 500:
                    X.pop(0)
                    Y0.pop(0)
                    Y1.pop(0)
                    Y2.pop(0)

            if i%20==0:
                lines[0].set_data(X, Y0)
                lines[1].set_data(X, Y1)
                lines[2].set_data(X, Y2)
                ax.autoscale()
                ax.relim()
                fig.canvas.draw()
                fig.canvas.flush_events()
                plt.pause(0.001)

    except KeyboardInterrupt:
        plt.close('all')
        m({"set": {"period": 1.}})
        break

plt.close('all')
m({"set": {"period": 1.}})
