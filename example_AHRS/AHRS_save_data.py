import os
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

for i in range(1000):
    sleep(1.)
    m({"set": {"period": 0.001}})
    try:
        t = m.get("time_ns")
        print(t)
        if t:
            break
    except:
        pass
    # m({"setLowPass": 1.})
# -------------------------------------------------------- #

minmax_mag = [[100, -100], [100, -100], [100, -100]]


def update_minmax_mag(mag):
    global minmax_mag
    for i in range(3):
        if mag[i] < minmax_mag[i][0]:
            minmax_mag[i][0] = mag[i]
        if mag[i] > minmax_mag[i][1]:
            minmax_mag[i][1] = mag[i]


# -------------------------------------------------------- #
t_ns = 0
t_ns_last = 0
data = []
count = 0
while True:
    sleep(0.001)
    try:
        t_ns = m.get("time_ns")
        if t_ns and t_ns is not t_ns_last:
            # print(count)
            t_ns_last = t_ns
            data.append(m().copy())
            # 中心の計算
            mag = m.get("mag")
            update_minmax_mag(mag)
            # print(count, "minmax_mag = ", minmax_mag)
            # print(m())
            count = count + 1
    except:
        pass
    if count > 1000:
        break

fdir = os.path.dirname(__file__)
f = open(fdir+"/dataAHRS.json", "w")
json.dump(data, f, ensure_ascii=True)
f.close()

# -------------------------------------------------------- #
