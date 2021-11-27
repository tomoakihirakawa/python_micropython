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
# -------------------------------------------------------- #
m = MediatorUDP(remote="192.168.1.40")
m({"set": {"period": 0.02}})
m({"setLowPass": 0.5})
# ------------------------------------------------------ #
start = time_ns()
# ------------------------- 図 ------------------------- #
fig = plt.figure()  # 図を生成
ax3d = fig.add_subplot(111, projection='3d')  # fig内部に軸を生成
r = [-3., 3.]  # range
ax3d.set_xlim(r)
ax3d.set_ylim(r)
ax3d.set_zlim(r)
sc = ax3d.scatter([0.], [0.], [0.])
DATA = [[], [], []]
while True:
    data = m.get("accel")
    current_time = (time_ns()-start)*10**-9
    DATA[0].append(data[0])  # 図用にmagにデータを蓄積
    DATA[1].append(data[1])  # 図用にmagにデータを蓄積
    DATA[2].append(data[2])  # 図用にmagにデータを蓄積
    sc._offsets3d = (DATA[0], DATA[1], DATA[2])
    ax3d.relim()
    ax3d.autoscale_view(True, True, True)
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.pause(0.1)
