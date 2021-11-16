from math import pi, sin
from openNetwork import *
m = MediatorUDP(remote="10.0.1.5")

# -------------------------------------------------------- #
T = 5  # 周期[sec]
c = 0.008*30/(2*pi)  # [m/rad] -> 1回転で進む距離は2*pi*c
L = 0.5   # 変位の振幅 [m]
# -------------------------------------------------------- #
n = 1600  # ドライバーに書いてある1回転に必要なステップ数 [setp/rotation]

a = L*n/(2*T*c)  # f = a*sin(w*t) [Hz] の a
# m({"freq": 1600})
m({"start_wave": (a, T)})
