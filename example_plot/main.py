'''
時間をかけないと身につきません．
自分の手で打ち込んでください．
'''
from math import sin
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Times New Roman"


def linspace(s, e, n):
    d = (e-s)/(n-1)
    return [s+d*i for i in range(n)]


X = linspace(0, 10, 100)
Y = []

for x in X:
    Y.append(sin(x))

fig, ax = plt.subplots()
ax.set(xlabel='time [s]', ylabel='wave height [m]')
ax.plot(X, Y)
plt.show()
