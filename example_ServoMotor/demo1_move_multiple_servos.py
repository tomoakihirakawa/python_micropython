'''DOC_EXTRACT servomotor

## 複数のサーボモーターの制御

やり方は，サーボモーター一つの場合と同じ．
これは，配列にサーボモーターのインスタンスを格納して実行した例．

'''

from lib.servomotor import *
from time import sleep, time_ns
import math

s = [servomotor(0, 0), servomotor(1, 0), servomotor(2, 0)]

start = time_ns()

while True:
    t = 2*(time_ns() - start)*10**-9
    s[0].setDegree(90+50*math.sin(t))
    s[1].setDegree(90+50*math.sin(t))
    s[2].setDegree(90+50*math.sin(t))
    sleep(0.001)
