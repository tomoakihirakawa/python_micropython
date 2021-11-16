from time import sleep, time
from servomotor import *
from AHRS import *
from fusion import *
from matplotlib.colors import Normalize
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.gridspec import GridSpec
import math

mid = 84
[s0, s1] = [servomotor(0), servomotor(1)]
s0.setDegree(mid)
s1.setDegree(mid)
sleep(0.5)
# -------------------------------------------------------- #
AHRS = MPU9250()
M = [[1.0071357813640687, 0.04763552506270946, -0.0038470932631186365, -0.01596407809200687],
     [-0.013128733223069055, 1.0047024495801606, 1.00470774203649449, -0.009469731551468645],
     [-0.0310392955158042, -0.04326700356018176, 0.9730776815049527, 0.004458175654467045]]
AHRS.MPU6050.set_M(M)
AHRS.MPU6050.calibrate_gyro()
# 
newoffset =  [3.27484130859375, 1.128997802734375, 0.007476806640625]
newscale =  [1.0405643738977073, 1.095636025998143, 0.8878856282919488]
AHRS.AK8963.setOffset(newoffset)
AHRS.AK8963.setScale(newscale)
# AHRS.MPU6050.calibrate_gyro()
# AHRS.AK8963.calibrate_visually(10)
# -------------------------------------------------------- #
sleep(0.5)
# -------------------------------------------------------- #
s = time()
t = s
q = [1, 0, 0, 0]  # クォータニオン初期値（適当に）
theta = -54  # 磁場の角度
Fusion = fusion(q, theta)  # 重力や磁場の情報から姿勢を計算するfusionクラス
count = 0
w = 0
while count < 10000:
    count += 1
    # sleep(0.02)
    accel = AHRS.accel()
    mag = AHRS.mag()
    gyro = AHRS.gyro()
    # -------------------------------------------------------- #
    dt = time() - t
    Fusion.update2(accel, mag, gyro, dt)
    [vx, vy, vz] = Fusion.Rs([0, 0, -1])
    print([vx, vy, vz])
    theta = math.atan2(vz, vx)/math.pi*180 + 5
    t = time()

    a = 5
    b = 0.05
    [wx, wy, wz] = AHRS.gyro()
    w = wy
    print(["w=", w, ", theta = ", theta, "a*w - b*theta=", a*w - b*theta])
    tmp = (a*w - b*theta**3)
    if tmp >= 85.:
        tmp = 85.
    if tmp <= -85.:
        tmp = -85.
    s0.setDegree(mid - tmp)
    s1.setDegree(mid + tmp)


s0.setDegree(mid)
s1.setDegree(mid)
