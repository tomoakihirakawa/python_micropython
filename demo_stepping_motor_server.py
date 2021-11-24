from math import pi, sin
from openNetwork import *
m = MediatorUDP(remote="10.0.1.4")

# -------------------------------------------------------- #
T = 10  # 周期[sec]
c = 0.06/(2*pi)  # [m/rad] -> 1回転で進む距離は2*pi*c
L = 0.1   # 変位の振幅 [m]
# -------------------------------------------------------- #
n = 6400  # ドライバーに書いてある1回転に必要なステップ数 [step/rotation]


a = L*n/(2*T*c)  # f = a*sin(w*t) [Hz] の a
# m({"freq": 1600})

print("最大速度", c*a*2.*pi/n)

m({"start_wave": (a, T)})
