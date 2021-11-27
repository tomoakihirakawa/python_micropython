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
# -------------------------------------------------------- #

t_ns = 0
t_ns_last = 0
data = []
count = 0
while True:
    sleep(0.03)
    try:
        t_ns = m.get("time_ns")
        print(m.get("mag"))
        if t_ns and t_ns is not t_ns_last:
            # print(count)
            t_ns_last = t_ns
            data.append(m().copy())
            count = count + 1
    except:
        pass
    if count > 10000:
        break

f = open("./dataAHRS.json", "w")
json.dump(data, f, ensure_ascii=True)
f.close()

# -------------------------------------------------------- #
