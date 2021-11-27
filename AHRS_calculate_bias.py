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
m({"set": {"period": 0.02}})
m({"setLowPass": 0.5})
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
for i in range(1000):
    sleep(0.02)
    try:
        accel = m.get("accel")
        mag = m.get("mag")
        update_minmax_mag(mag)
        gyro = m.get("gyro")
        current_time = (time_ns()-start)*10**-9
        X3d.append(gyro[0])
        Y3d.append(gyro[1])
        Z3d.append(gyro[2])
        data = mag  # @ データを選択
        bias = [0.1*bias[0]+0.9*data[0],
                0.1*bias[1]+0.9*data[1],
                0.1*bias[2]+0.9*data[2]]
        print("bias= ", minmax_mag)
    except:
        print("error")
        pass
m({"set": {"period": 1.}})

fig = plt.figure()  # 図を生成
ax3d = fig.add_subplot(111, projection='3d')  # fig内部に軸を生成
sc = ax3d.scatter(X3d, Y3d, Z3d)
ax3d.relim()
ax3d.autoscale_view(True, True, True)
plt.show(block=False)
plt.pause(10)
# -------------------------------------------------------- #
