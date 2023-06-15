import ctypes
from time import sleep
import smbus
from servomotor import *
from time import sleep, time_ns
import json
import math
import matplotlib.pyplot as plt
plt.rcParams.update({"font.family": "Times New Roman", 'font.size': 20})


def tToi(tIN, w, data_size):
    f = w / (2.*math.pi)
    T = 1/f
    t = tIN - T*math.floor(tIN/T)  # モジュロー
    i = round(data_size*t/T)
    if i < 0 or i >= data_size:
        return 0
    else:
        X.append(row[0])
        return i

# ------------------ JSONファイルの読み込みをチェック ------------------ #


n = 7
data_size = 0
X = []
Q0 = []
Q1 = []
Q2 = []
Q3 = []
Q4 = []
Q5 = []
Q6 = []
# with open("/home/pi/Desktop/c1,c2=0.01~0.15/c1_0.05_c2_0.1_ck0.9.json", 'r') as json_file:
with open("c1_0.01_c2_0.01_ck0.6.json", 'r') as json_file:
    data = json.load(json_file)
    timeVSangle = data["timeVSangle"]
    parames = data["params"]
    data_size = len(timeVSangle)
    for row in timeVSangle:
        X.append(row[0])
        Q0.append(row[1][0])
        Q1.append(row[1][1])
        Q2.append(row[1][2])
        Q3.append(row[1][3])
        Q4.append(row[1][4])
        Q5.append(row[1][5])
        Q6.append(row[1][6])

print(parames)

r = parames["r"]
w = parames["w"]
L = parames["L"]
c1 = parames["c1"]
c2 = parames["c2"]


# ---------------------- Mathematicaで計算したデータの参照のチェック ---------------------- #

# T = []
# Qs = [[], [], [], [], [], [], []]

# for i in range(200):
#     t = i/100.
#     index = tToi(t, w, data_size)

#     Qs[0].append(Q0[index])
#     Qs[1].append(Q1[index])
#     Qs[2].append(Q2[index])
#     Qs[3].append(Q3[index])
#     Qs[4].append(Q4[index])
#     Qs[5].append(Q2[index])
#     Qs[6].append(Q6[index])

#     T.append(t)
#     print(index, t)

#! -------------------------------------------------------- #
#! 忘れずに servomotor package をこのディレクトリに保存しておくこと

s0 = servomotor(0, 0)
s1 = servomotor(2, 0)
s2 = servomotor(4, 0)
s3 = servomotor(6, 0)
s4 = servomotor(8, 0)
s5 = servomotor(10, 0)
s6 = servomotor(12, 0)

b0 = 90
b1 = 90
b2 = 95
b3 = 90
b4 = 90
b5 = 85
b6 = 90

s0.setDegree(b0)
s1.setDegree(b1)
s2.setDegree(b2)
s3.setDegree(b3)
s4.setDegree(b4)
s5.setDegree(b5)
s6.setDegree(b6)


sleep(4)
start = time_ns()
c = 180./math.pi


i2c = smbus.SMBus(1)


INA226_ADDRESS = 0x40


# print("Configuring INA226..")
# iSensor = ina226(INA226_ADDRESS,1)
# iSensor.configure()
# iSensor.calibrate(rShuntValue = 0.002, iMaxExcepted = 10)

# sleep(1)

# # print "Configuration Done"

# current = iSensor.readShuntCurrent()

# print("Current Value is ",str(current),"A")

# print "Mode is "+str(hex(iSensor.getMode()))

# A = 0
# P = 0
# V = 0
# a = 0.6
# count = 0
while True:
    sleep(0.001)
    t = -(time_ns() - start)*10**-9
    index = tToi(t, w*1., data_size)
    s0.setDegree(Q0[index]*c + b0)
    s1.setDegree(Q1[index]*c + b1)
    s2.setDegree(Q2[index]*c + b2)
    s3.setDegree(Q3[index]*c + b3)
    s4.setDegree(Q4[index]*c + b4)
    s5.setDegree(Q5[index]*c + b5)
    s6.setDegree(Q6[index]*c + b6)

#     V = V*(1-a) + iSensor.readBusVoltage() *a
#     P = P*(1-a) + iSensor.readBusPower() *a
#     A = A*(1-a) +  iSensor.readShuntCurrent()*a
#     if count is 10 :
#         print("V = ", V, ", A = ",A, ", P = ", P)
#         count = 0
#     count = 1 + count
