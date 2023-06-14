import matplotlib.pyplot as plt
from lib.openNetwork import *
from math import pi, sin
from statistics import mean
import json
from integrator import *
from fundamental import *
from time import time, sleep, time_ns
import numpy as np
from matplotlib.gridspec import GridSpec
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import Normalize
import matplotlib
from matplotlib import pyplot as plt
matplotlib.rcParams['font.family'] = 'Times New Roman'

# -------------------------------------------------------- #
# m = MediatorUDP(remote="192.168.11.12")
m = MediatorUDP(remote="10.0.1.21")
for i in range(10):
    sleep(0.1)
    m({"set": {"period": 0.01}})
    # m({"setLowPass": 0.1})
# -------------------------------------------------------- #
start = time_ns()
bias = [0, 0, 0]

minmax_mag = [[100, -100], [100, -100], [100, -100]]


def update_minmax_mag(mag):
    global minmax_mag
    for i in range(3):
        if mag[i] < minmax_mag[i][0]:
            minmax_mag[i][0] = mag[i]
        if mag[i] > minmax_mag[i][1]:
            minmax_mag[i][1] = mag[i]


# -------------------------------------------------------- #
X3d = []
Y3d = []
Z3d = []
fig = plt.figure()  # 図を生成
ax3d = fig.add_subplot(111, projection='3d')  # fig内部に軸を生成
sc = ax3d.scatter(X3d, Y3d, Z3d)

accel=[0,0,0]
mag=[0,0,0]
gyro=[0,0,0]
for i in range(100000):
    sleep(0.01)
    try:
        tmp = (0.9*accel[0]+0.1*m.get("accel")[0],
                0.9*accel[1]+0.1*m.get("accel")[1],
                0.9*accel[2]+0.1*m.get("accel")[2])
        accel = tmp
        print(accel)
        print(m.get("accel"))
        mag = (0.9*mag[0]+0.1*m.get("mag")[0],
                0.9*mag[1]+0.1*m.get("mag")[1],
                0.9*mag[2]+0.1*m.get("mag")[2])
        update_minmax_mag(mag)
        gyro = (0.9*gyro[0]+0.1*m.get("gyro")[0],
                0.9*gyro[1]+0.1*m.get("gyro")[1],
                0.9*gyro[2]+0.1*m.get("gyro")[2])
        current_time = (time_ns()-start)*10**-9

        bias_mag = ((minmax_mag[0][1]+minmax_mag[0][0])/2,
                    (minmax_mag[1][1]+minmax_mag[1][0])/2,
                    (minmax_mag[2][1]+minmax_mag[2][0])/2)

        X3d.append(mag[0]-bias_mag[0])
        Y3d.append(mag[1]-bias_mag[1])
        Z3d.append(mag[2]-bias_mag[2])

        data = gyro  # @ データを選択

        bias = [0.1*bias[0]+0.9*data[0],
                0.1*bias[1]+0.9*data[1],
                0.1*bias[2]+0.9*data[2]]
        print("mag=", mag, "minmax= ", minmax_mag, "data", data, "gyro", gyro, "accel", accel)

        if len(X3d) > 1000:
            X3d.pop(0)
            Y3d.pop(0)
            Z3d.pop(0)

        sc._offsets3d = (X3d, Y3d, Z3d)        
        ax3d.autoscale_view(True, True, True)
        ax3d.set_xlim([-2.5, 2.5])
        ax3d.set_ylim([-2.5, 2.5])
        ax3d.set_zlim([-2.5, 2.5])
        fig.canvas.draw()
        fig.canvas.flush_events()
        plt.pause(0.001)

        
    except:
        print("error")
        pass
m({"set": {"period": 1.}})
# -------------------------------------------------------- #
