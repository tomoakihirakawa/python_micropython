from lib.openNetwork import *
from time import time, sleep

m = MediatorUDP(remote="10.0.1.10")
m({"makeservo": 0})
# m({"makeservo": 1})
# m({"makeservo": 2})
for j in range(100):
    for i in range(0, 180, 180):
        sleep(3)
        print(i)
        m({"setDegree0": i})
    for i in range(180, 0, -180):
        sleep(3)
        print(i)
        m({"setDegree0": i})

# m({"repeateMoveAll": (100, 85, 100, 500)})

# for i in range(10):
#     sleep(.5)
#     m({"setDegree1": 80})
#     m({"setDegree2": 80})
#     sleep(.5)
#     m({"setDegree1": 100})
#     m({"setDegree2": 100})

# m({"setDegree1": 90})
