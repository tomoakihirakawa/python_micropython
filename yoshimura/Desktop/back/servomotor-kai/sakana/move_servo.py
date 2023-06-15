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
    if i >= data_size or i < 0:
        return 0
    else:
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
with open("./each_timeVSangle_c1_0.05_c2_0.05_w1.2.json", 'r') as json_file:
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

T = []
Qs = [[], [], [], [], [], [], []]
for i in range(200):
    t = i/100.
    index = tToi(t, w, data_size)

    Qs[0].append(Q0[index])
    Qs[1].append(Q1[index])
    Qs[2].append(Q2[index])
    Qs[3].append(Q3[index])
    Qs[4].append(Q4[index])
    Qs[5].append(Q2[index])
    Qs[6].append(Q6[index])

    T.append(t)
    print(index, t)
    print("Q6[index] = ",Q6[index])

#! -------------------------------------------------------- #
#! 忘れずに servomotor package をこのディレクトリに保存しておくこと

s0 = servomotor(0, 0)
s1 = servomotor(8, 0)
s2 = servomotor(2, 0)
s3 = servomotor(3, 0)
s4 = servomotor(4, 0)
s5 = servomotor(5, 0)
s6 = servomotor(6, 0)

sleep(1)

# for i in range(60,120,1):
#     sleep(.5)
#     print(i)
#     s0.setDegree(i)    

c = 180./math.pi

b0 = 90.
b1 = 90.
b2 = 95.
b3 = 90.
b4 = 90.
b5 = 85.
b6 = 90.

s0.setDegree(b0)        
s1.setDegree(b1)        
s2.setDegree(b2)        
s3.setDegree(b3)        
s4.setDegree(b4)        
s5.setDegree(b5)        
s6.setDegree(b6)      

sleep(1)

print("data_size",data_size)
c = 180./math.pi
start = time_ns()
while True:
    sleep(0.01)
    t = (time_ns() - start)*10**-9    
    index = tToi(t, w, data_size)
    s0.setDegree(c*Q0[index]+b0)        
    s1.setDegree(c*Q1[index]+b1)        
    s2.setDegree(c*Q2[index]+b2)        
    s3.setDegree(c*Q3[index]+b3)        
    s4.setDegree(c*Q4[index]+b4)        
    s5.setDegree(c*Q5[index]+b5)        
    s6.setDegree(c*Q6[index]+b6)        