from time import time, sleep
import matplotlib.pyplot as plt
from lib.openNetwork import *
from math import pi, sin
from time import time, sleep, time_ns
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
matplotlib.rcParams['font.family'] = 'Times New Roman'

# -------------------------------------------------------- #
#                     リモート計測機の設定                    #
# -------------------------------------------------------- #
remote_addr = ["192.168.11.3",
               "192.168.11.4",
               "192.168.11.7",
               "192.168.11.2",
               "192.168.11.9",
               "192.168.11.8",
               "192.168.11.6"]

#
# remote_addr = ["192.168.0.115",
#                "192.168.0.118",
#                "192.168.0.121",
#                   "192.168.0.119",
#                "192.168.0.123",
#                "192.168.0.122",
#                "192.168.0.120"]

# remote_addr = ["10.0.1.19",
#                "10.0.1.17",
#                "10.0.1.12",
#                "10.0.1.14",
#                "10.0.1.16",
#                "10.0.1.13",
#                "10.0.1.15"
#    ]


N_sensors = len(remote_addr)

sensors = [MediatorUDP(remote=remote_addr[i], port=i*1000+50000)
           for i in range(N_sensors)]

sleep(1.)

period = 0.001

print(sensors)

for i in range(20):
    for sen in sensors:
        sleep(0.1)
        sen({"set": {"period": period}})

# -------------------------------------------------------- #
#                           図の準備                         #
# -------------------------------------------------------- #
# 各センサーの図
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set(xlabel='time [s]', ylabel='pressure [kPa]')

Ps = [[] for i in range(N_sensors)]
T = []

colors = ['green', 'blue', 'red', 'yellow',
          'black', 'orange', 'magenta', 'cyan']

labels = ['s0', 's1', 's2', 's3', 's4', 's5', 's6']

lines = [ax.plot(T, Ps[i], '.-', color=colors[i], label=labels[i])[0]
         for i in range(N_sensors)]
# -------------------------------------------------------- #
# 各センサーのから求めた力の図
Fx = []
Fy = []
# 各センサーのから求めたz方向のモーメントの図
Nz = []

start = time_ns()
count = 0
# -------------------------------------------------------- #
B = 280/1000.  # 幅
L = [5/1000., 5/1000., 10/1000, 8/1000, 10/1000, 5/1000., 5/1000.]  # 各センサーのL高さ
A = [l*B for l in L]
#
SENSOR_XY = [[-0.14, 0.08], [-0.14, 0.03],
             [-0.08, 0.],
             [0., 0.],
             [0.08, 0.],
             [0.14, 0.03], [0.14, 0.08]]

N = [[1, 0], [1, 0],
     [0, 1],
     [0, 1],
     [0, 1],
     [-1, 0], [-1, 0]]  # 各センサーの向く単位法線ベクトル

CG = [0., 0.08]


R = [[SENSOR_XY[i][0]-CG[0], SENSOR_XY[i][1]-CG[1]]
     for i in range(len(SENSOR_XY))]
print("R", R)
F = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]

bias = [0, 0, 0, 0, 0, 0, 0]


def moment():
    global R
    global F
    ret = 0
    for i in range(len(F)):
        ret -= (R[i][0]*F[i][1]-R[i][1]*F[i][0])*A[i]
    return ret


# -------------------------------------------------------- #
#                        計測とプロット                       #
# -------------------------------------------------------- #
a = 0.01

while count < 500000:
    count += 1
    sleep(0.02)
    print(count)
    try:
        current_time = (time_ns()-start)*10**-9
        T.append(current_time)
        #$ -------------------------------------------------------- #
        #$                          各センサーの値                     #
        #$ -------------------------------------------------------- #
        for i in range(len(lines)):
            print(sensors[i]())
            value = sensors[i].get("p")
            print(value)
            if not value:
                value = 0

            if len(Ps[i]) > 0:
                tmp = (1-a)*bias[i] + a*value
            else:
                tmp = value

            bias[i] = tmp
            Ps[i].append(value-bias[i])
            lines[i].set_ydata(Ps[i])
            lines[i].set_xdata(T)

        print("bias = ", bias)
        ax.relim()
        ax.autoscale()
        fig.canvas.draw()

        plt.pause(0.001)
        plt.legend()

        # if len(T) > 100:
        #     T.pop(0)
        # for i in range(len(lines)):
        #     if len(Ps[i]) > 100:
        #         Ps[i].pop(0)

    except KeyboardInterrupt:
        plt.close('all')
        for i in range(30):
            sleep(0.1)
            for sen in sensors:
                sen({"set": {"period": 1.}})
        break


plt.close('all')
for i in range(30):
    sleep(0.1)
    for sen in sensors:
        sen({"set": {"period": 1.}})
