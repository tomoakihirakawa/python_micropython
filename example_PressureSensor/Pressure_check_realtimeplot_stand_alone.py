from time import time, sleep
import matplotlib.pyplot as plt
from math import pi, sin
from time import time, sleep, time_ns
import numpy as np
import matplotlib
from matplotlib import pyplot as plt
matplotlib.rcParams['font.family'] = 'Times New Roman'
red = "\033[31m"
blue = "\033[34m"
default = "\033[39m"
# -------------------------------------------------------- #
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set(xlabel='time [s]', ylabel='pressure [Pa]')
# -------------------------------------------------------- #
period = 0.01

N_sensors = 7

Ps = [[] for i in range(N_sensors)]
Ts = [[] for i in range(N_sensors)]

colors = ['green', 'blue', 'red', 'yellow',
          'black', 'orange', 'magenta', 'cyan']

lines = [ax.plot(Ts[i], Ps[i], color=colors[i], label=colors[i])[0]
         for i in range(N_sensors)]

start = time_ns()
count = 0
# -------------------------------------------------------- #
while count < 5000:
    count += 1
    sleep(period)
    print(count)
    try:
        current_time = (time_ns()-start)*10**-9
        data = {"depth": sin(current_time)}
        print(data)
        for i in range(len(lines)):
            Ps[i].append(data["depth"]*i)
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
        break
