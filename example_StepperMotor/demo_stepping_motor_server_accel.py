from math import pi, sin
from python_shared_lib.openNetwork import *
from time import sleep
# m = MediatorUDP(remote="192.168.11.2")
m = MediatorUDP(remote="10.0.1.20")

# -------------------------------------------------------- #
#                            命令                           #
# -------------------------------------------------------- #
# m({"start_asymptotic": 5000})

for i in range(100):
    sleep(2)
    m({"freq": 100000})
    sleep(2)
    m({"freq": -100000})
