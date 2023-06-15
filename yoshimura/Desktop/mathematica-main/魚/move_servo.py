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
    if i is 0 or i is data_size:
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
with open("./each_timeVSangle.json", 'r') as json_file:
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

#! -------------------------------------------------------- #
#! 忘れずに servomotor package をこのディレクトリに保存しておくこと

s = [servomotor(0, 0),
     servomotor(1, 0),
     servomotor(2, 0)]

time.sleep(1)

start = time_ns()
while True:
    t = (time_ns() - start)*10**-9
    for i in range(3):
        s[i].setDegree(Q0[tToi(t, w, data_size)])
