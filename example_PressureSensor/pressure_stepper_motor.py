import matplotlib.pyplot as plt
from lib.openNetwork import *
from math import pi, sin
from time import time, sleep, time_ns
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
matplotlib.rcParams['font.family'] = 'Times New Roman'
#% -------------------------------------------------------- #
m = MediatorUDP(remote="10.0.1.20")
#% -------------------------------------------------------- #
#%                            設定                          #
#% -------------------------------------------------------- #
T = 5  # % 周期[sec]
c = (78/10/1000)/(2*pi)  # % [m/rad] -> 1回転で進む距離は2*pi*c
L = 0.1  # % 変位の振幅 [m]
n = 6400  # % ドライバーに書いてある1回転に必要なステップ数 [step/rotation]
#% -------------------------------------------------------- #
a = L*n/(2*T*c)  # %f = a*sin(w*t) [Hz] の a
# m({"freq": 1600})
print("最大速度", c*a*2.*pi/n)
#% -------------------------------------------------------- #
#%                            命令                           #
#% -------------------------------------------------------- #
# m({"freq": 1000})
m({"start_cos_wave": (a, T)})
# m({"start_sin_wave": (a, T)})

#$ -------------------------------------------------------- #
#$                     リモート計測機の設定                    #
#$ -------------------------------------------------------- #
# remote_addr = ["192.168.0.115",
#                "192.168.0.125",
#                "192.168.0.15",
#                "192.168.0.115",
#                "192.168.0.415",
#                "192.168.0.115"]

remote_addr = ["10.0.1.19",
               "10.0.1.17",
               "10.0.1.12",
               "10.0.1.14",
               "10.0.1.16",
               "10.0.1.13",
               "10.0.1.15"]

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

while count < 5000:
    count += 1
    sleep(period)
    print(count)
    try:
        current_time = (time_ns()-start)*10**-9
        for i in range(len(lines)):
            Ps[i].append(sensors[i].get("depth"))
            Ts[i].append(current_time)
            lines[i].set_ydata(Ps[i])
            lines[i].set_xdata(Ts[i])

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
