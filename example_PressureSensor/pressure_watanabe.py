import csv
from os import stat_result
import matplotlib.pyplot as plt
from lib.openNetwork import *
from math import pi, sin
from time import time, sleep, time_ns
import numpy as np
import math
import matplotlib
from matplotlib import pyplot as plt
# matplotlib.rcParams['font.family'] = 'Times New Roman'

#$ -------------------------------------------------------- #
#$                     リモート計測機の設定                    #
#$ -------------------------------------------------------- #

remote_addr = ["192.168.11.2"]

N_sensors = len(remote_addr)

sensors = [MediatorUDP(remote=remote_addr[i], port=(i+1)*1000+50000)
           for i in range(N_sensors)]

sleep(1.)

period = 0.0

for i in range(20):
    sleep(0.1)
    for sen in sensors:
        sen({"set": {"period": period}})

sleep(1.)
#$ -------------------------------------------------------- #
#$ -------------------------------------------------------- #


#% -------------------------------------------------------- #
m = MediatorUDP(remote="192.168.11.7")
#% -------------------------------------------------------- #
#%                            設定                          #
#% -------------------------------------------------------- #
h = 0.1
L = 0.25  # % 変位の振幅 [m]
g = 9.8
w = 1*math.sqrt(pi*g/L*math.tanh(pi*h/L))
c = (78/10/1000)/(2*pi)  # % [m/rad] -> 1回転で進む距離は2*pi*c
T = 2*pi/w  # % 周期[sec]
n = 6400  # % ドライバーに書いてある1回転に必要なステップ数 [step/rotation]
A = 0.01
a = A*n/(2*T*c)  # %f = a*sin(w*t) [Hz] の a
# m({"freq": 1600})
print("最大速度", c*a*2.*pi/n)
print("T = ", T, ", a = ", a)
## -------------------------------------------------------- #
##                           図の準備                        #
## -------------------------------------------------------- #
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set(xlabel='time [s]', ylabel='pressure [kPa]')
Ps = [[] for i in range(N_sensors)]
Ts = [[] for i in range(N_sensors)]
colors = ['green', 'blue', 'red', 'yellow',
          'black', 'orange', 'magenta', 'cyan']
labels = ['s0', 's1', 's2', 's3', 's4', 's5', 's6']
lines = [ax.plot(Ts[i], Ps[i], color=colors[i], label=labels[i])[0]
         for i in range(N_sensors)]
start = time_ns()
count = 0
## -------------------------------------------------------- #
##                        計測とプロット                      #
## -------------------------------------------------------- #
b = 1.
# ローパスなし　+-0.05

# m({"freq": 0})


def Mean(V):
    ret = 0
    for i in range(len(V)):
        ret += V[i]
    return ret/len(V)


def Subtract(V, mean):
    return [V[i]-mean for i in range(len(V))]


started = False
sleep(.5)
offset = 0
while count < 5000:
    count += 1
    sleep(period)
    #% -------------------------------------------------------- #
    #%                            命令                           #
    #% -------------------------------------------------------- #
    # m({"freq": 1000})
    if not started and (time_ns() - start)*10**-9 > 2:
        m({"sin_wave": (a, T, 10*T)})
        print("start!!")
        print("T = ", T, ", a = ", a)
        started = True
        offset = Mean(Ps[0])
        print("offset=", offset)

    # m({"start_sin_wave": (a, T)})
    # print(count)
    try:
        current_time = (time_ns()-start)*10**-9

        if current_time > 10:
            break

        i = 0
        Ps[i].append(sensors[i].get("p"))
        Ts[i].append(current_time)
        lines[i].set_ydata(Ps[i])
        lines[i].set_xdata(Ts[i])

        ax.relim()
        ax.autoscale()
        fig.canvas.draw()
        plt.pause(0.001)
        plt.legend()
    except KeyboardInterrupt:

        with open("./pressure.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerow(Ts[0])
            writer.writerow(Subtract(Ps[0], offset))
        for i in range(10):
            sleep(.1)
            m({"freq": 0})
        plt.close('all')

        for i in range(10):
            sleep(0.1)
            for sen in sensors:
                sen({"set": {"period": 1.}})

        break


with open("./pressure.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerow(Ts[0])
    writer.writerow(Subtract(Ps[0], offset))
    print("data ", len(Ps[0]))
for i in range(10):
    sleep(.1)
    m({"freq": 0})
plt.close('all')

for i in range(10):
    sleep(0.1)
    for sen in sensors:
        sen({"set": {"period": 1.}})
