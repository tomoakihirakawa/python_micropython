from openNetwork import *
from time import time, sleep

m = MediatorUDP(remote="192.168.0.101")
# m({"makeservo": 0})
m({"makeservo": 1})
# m({"makeservo": 2})
m({"setDegree1": 90})
m({"repeateMoveAll": (100, 85, 100, 500)})


# for i in range(10):
#     sleep(.5)
#     m({"setDegree1": 80})
#     m({"setDegree2": 80})
#     sleep(.5)
#     m({"setDegree1": 100})
#     m({"setDegree2": 100})

m({"setDegree1": 90})
