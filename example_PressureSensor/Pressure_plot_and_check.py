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

# remote_addr = ["10.0.1.19",
#    "10.0.1.17",
#    "10.0.1.12",
#    "10.0.1.14",
#    "10.0.1.16",
#    "10.0.1.13",
#    "10.0.1.15"
#    ]

N_sensors = len(remote_addr)

sensors = [MediatorUDP(remote=remote_addr[i], port=i*1000+50000)
           for i in range(N_sensors)]

sleep(1.)

period = 0.005

print(sensors)

for i in range(10):
    for sen in sensors:
        sleep(.1)
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
fig_sum = plt.figure()
ax_sum = fig_sum.add_subplot(111)
ax_sum.set(xlabel='time [s]', ylabel='force [kN]')
lines_sum_x = ax_sum.plot(T, Fx)[0]
lines_sum_y = ax_sum.plot(T, Fy)[0]
# -------------------------------------------------------- #
# 各センサーのから求めたz方向のモーメントの図
Nz = []
fig_moment = plt.figure()
ax_moment = fig_moment.add_subplot(111)
ax_moment.set(xlabel='time [s]', ylabel='moment [N m]')
lines_moment = ax_moment.plot(T, Nz)[0]
# -------------------------------------------------------- #

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
past = 0
now = 0
bias = [102.75460460252943, 102.74075176852891, 101.06685097576269,
        100.63456659343748, 102.03316073220265, 102.41707749128749, 102.86334356599812]
a = 0.5
while count < 500000:
    count += 1
    # sleep(period)
    print(count)
    try:
        now = time_ns()
        dt = (now-past)*10**-9
        current_time = (now-start)*10**-9
        T.append(current_time)
        past = now
        print("dt = ", dt)
        #$ -------------------------------------------------------- #
        #$                          各センサーの値                     #
        #$ -------------------------------------------------------- #
        for i in range(N_sensors):
            value = sensors[i].get("p")
            if len(Ps[i]) > 0:
                tmp = (1-a)*Ps[i][-1] + a*(value-bias[i])
            else:
                tmp = value-bias[i]
            Ps[i].append(tmp)
            lines[i].set_ydata(Ps[i])
            lines[i].set_xdata(T)
        ax.relim()
        ax.autoscale()
        fig.canvas.draw()
        ## -------------------------------------------------------- #
        ##                           力の計算                        #
        ## -------------------------------------------------------- #
        # まずは，各センサーにかかる力のxy成分を足し合わせる
        Fx_ = 0
        Fy_ = 0
        for i in range(len(sensors)):
            p = sensors[i].get("p")
            if p is None:
                p = 0
            f = A[i]*p
            F[i] = [f*N[i][0], f*N[i][1]]
            Fx_ += F[i][0]
            Fy_ += F[i][1]
        # 足し合わせた結果を格納
        Fx.append(Fx_)
        Fy.append(Fy_)
        # 図に表示させるデータ数
        lines_sum_x.set_ydata(Fx)
        lines_sum_x.set_xdata(T)
        lines_sum_y.set_ydata(Fy)
        lines_sum_y.set_xdata(T)

        ax_sum.relim()
        ax_sum.autoscale()
        fig_sum.canvas.draw()
        #% -------------------------------------------------------- #
        #%                    モーメントの計算                        #
        #% -------------------------------------------------------- #
        # まずは，各センサーにかかる力のxy成分を足し合わせる
        nz = moment()
        # 足し合わせた結果を格納
        Nz.append(nz)
        lines_moment.set_ydata(Nz)
        lines_moment.set_xdata(T)

        ax_moment.relim()
        ax_moment.autoscale()
        fig_moment.canvas.draw()
        # -------------------------------------------------------- #

        if count > 100:
            T.pop(0)
            for i in range(len(lines)):
                Ps[i].pop(0)
            Fx.pop(0)
            Fy.pop(0)
            Nz.pop(0)

        plt.pause(0.001)
        plt.legend()
    except KeyboardInterrupt:
        plt.close('all')
        for i in range(30):
            sleep(0.1)
            for sen in sensors:
                sen({"set": {"period": 1.}})
        break
