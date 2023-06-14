import matplotlib.pyplot as plt
from lib.openNetwork import *
from math import pi, sin
from time import time, sleep, time_ns
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
matplotlib.rcParams['font.family'] = 'Times New Roman'
#% -------------------------------------------------------- #
m = MediatorUDP(remote="192.168.11.14")
m({"makeservo": 0})
#$ -------------------------------------------------------- #
#$                     リモート計測機の設定                    #
#$ -------------------------------------------------------- #
remote_addr = ["192.168.11.3",
               "192.168.11.4",
               "192.168.11.7",
               "192.168.11.2",
               "192.168.11.9",
               "192.168.11.8",
               "192.168.11.6"]

# remote_addr = ["10.0.1.19",
#                "10.0.1.17",
#                "10.0.1.12",
#                "10.0.1.14",
#                "10.0.1.16",
#                "10.0.1.13",
#                "10.0.1.15"]

N_sensors = len(remote_addr)

sensors = [MediatorUDP(remote=remote_addr[i], port=(i+1)*1000+50000)
           for i in range(N_sensors)]

sleep(1.)

period = 0.05

for i in range(10):
    sleep(0.1)
    for sen in sensors:
        sen({"set": {"period": period}})

sleep(1.)

#$ -------------------------------------------------------- #
#$                           図の準備                        #
#$ -------------------------------------------------------- #

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set(xlabel='time [s]', ylabel='pressure [kPa]')
#$ -------------------------------------------------------- #

Ps = [[] for i in range(N_sensors)]
Ts = [[] for i in range(N_sensors)]

colors = ['green', 'blue', 'red', 'yellow',
          'black', 'orange', 'magenta', 'cyan']

labels = ['s0', 's1', 's2', 's3', 's4', 's5', 's6']

lines = [ax.plot(Ts[i], Ps[i], color=colors[i], label=labels[i])[0]
         for i in range(N_sensors)]

start = time_ns()
count = 0

#$ -------------------------------------------------------- #
#$                        計測とプロット                      #
#$ -------------------------------------------------------- #
bias = [102.75460460252943, 102.74075176852891, 101.06685097576269,
        100.63456659343748, 102.03316073220265, 102.41707749128749, 102.86334356599812]
a = 0.5

while count < 5000:
    count += 1
    sleep(period)
    # print(count)
    sum = 0
    try:
        current_time = (time_ns()-start)*10**-9
        for i in range(len(lines)):
            value = sensors[i].get("p")
            if len(Ps[i]) > 0:
                tmp = (1-a)*Ps[i][-1] + a*(value-bias[i])
            else:
                tmp = value-bias[i]
            sum = sum + tmp
            Ps[i].append(tmp)
            Ts[i].append(current_time)
            lines[i].set_ydata(Ps[i])
            lines[i].set_xdata(Ts[i])
        # -------------------------------------------------------- #
        deg = sum*50-100
        print("deg", deg)
        m({"setDegreeAll": deg})
        # -------------------------------------------------------- #
        ax.relim()
        ax.autoscale()
        fig.canvas.draw()
        plt.pause(0.001)
        plt.legend()
    except KeyboardInterrupt:
        plt.close('all')
        for i in range(10):
            sleep(0.1)
            for sen in sensors:
                sen({"set": {"period": 1.}})

        break
