import matplotlib.pyplot as plt
from time import time, sleep


from time import time, sleep
from openNetwork import *

sensors = []
sensors.append(MediatorUDP(remote="192.168.0.115", port=50000))
sensors.append(MediatorUDP(remote="192.168.0.102", port=51000))
sensors.append(MediatorUDP(remote="192.168.0.103", port=52000))
sensors.append(MediatorUDP(remote="192.168.0.104", port=53000))
sensors.append(MediatorUDP(remote="192.168.0.105", port=54000))

sleep(1.)
period = 0.07
for i in range(len(sensors)):
    sensors[i]({"set": {"period": period}})
sleep(1.)
# -------------------------------------------------------- #
fig = plt.figure()
ax = fig.add_subplot()
ax_ = []
ax.set_xlim([0., 1.])
ax.set_ylim([-10., 10.])

P = []
T = []

colors = ['green', 'blue', 'red', 'yellow', 'black']
for i in range(len(sensors)):
    # アップデートするためにデータを取り出す？
    ax_.append(ax.plot([], [], color=colors[i])[0])
    P.append([])
    T.append([])
# -------------------------------------------------------- #
s = time()
count = 0
while count < 5000:
    count += 1
    sleep(period)
    print(count)
    for i in range(len(sensors)):
        try:
            data = sensors[i]()
            print(data)
            P[i].append(data["depth"])
            T[i].append(time()-s)
            print(T[i][-1], P[i][-1])
            ax_[i].set_xdata(T[i])
            ax_[i].set_ydata(P[i])
        except:
            pass
        try:
            ax.set_xlim(T[i][0], T[i][-1])
        except:
            pass

    plt.pause(0.001)
