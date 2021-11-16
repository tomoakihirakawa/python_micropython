from math import pi, sin
from openNetwork import *
m = MediatorUDP(remote="10.0.1.5")

# -------------------------------------------------------- #
T = 5  # [sec]
c = 0.008*30/(2*pi)  # [m/rad]
# テスト
L = 0.5   # [m]
print(L)

# -------------------------------------------------------- #
n = 1600  # [setp/rotation]
a = L*n/(2*T*c)

# m({"freq": 1600})
m({"start_wave": (a, T)})
