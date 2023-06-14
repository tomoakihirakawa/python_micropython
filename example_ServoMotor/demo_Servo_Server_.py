from lib.openNetwork import *
from time import time, sleep

m = MediatorUDP(remote="192.168.0.113")
m({"makeservo": 0})
# m({"makeservo": 1})
# m({"makeservo": 2})
for i in range(10):
    m({"setDegreeAll": 0})
    sleep(3)
    m({"setDegreeAll": 180})
    sleep(3)
# for i in range(0, 180, 5):
#     sleep(.2)
#     m({"setDegreeAll": i})
# for i in range(180, 0, -5):
#     sleep(.2)
#     m({"setDegreeAll": i})

# m({"repeateMoveAll": (100, 85, 100, 500)})

# for i in range(10):
#     sleep(.5)
#     m({"setDegree1": 80})
#     m({"setDegree2": 80})
#     sleep(.5)
#     m({"setDegree1": 100})
#     m({"setDegree2": 100})

# m({"setDegree1": 90})
