from matplotlib.colors import Normalize
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.gridspec import GridSpec
import math
import numpy as np
# import imu
from fusion import *
from time import time, sleep
from fundamental import *

# AHRS = imu.mpu9250()

# M = [[1.0071357813640687, 0.04763552506270946, -0.0038470932631186365, -0.01596407809200687],
#      [-0.013128733223069055, 1.0047024495801606,
#          0.00470774203649449, -0.009469731551468645],
#      [-0.0310392955158042, -0.04326700356018176, 0.9730776815049527, 0.004458175654467045]]
# AHRS.mpu6050.set_M(M)
# AHRS.mpu6050.calibrate_gyro()
# # AHRS.ak8963.setOffset([0.85, -1.35, 1.4])
# AHRS.ak8963.calibrate_visually(10)
# -------------------------------------------------------- #
fig = plt.figure()  # 図を生成
gs = GridSpec(nrows=2, ncols=2)
minmax = [-1.1, 1.1]
# ------------------------- 図の設定 ------------------------- #
xy = fig.add_subplot(gs[0, 0])  # fig内部に軸を生成
xy.set_xlim(minmax)
xy.set_ylim(minmax)
xy.set_xlabel('X')
xy.set_ylabel('Y')
xy_ = xy.quiver(0., 0., 0., 0., color="blue",angles='xy', scale_units='xy', scale=1)

yz = fig.add_subplot(gs[0, 1])  # fig内部に軸を生成
yz.set_xlim(minmax)
yz.set_ylim(minmax)
yz.set_xlabel('Y')
yz.set_ylabel('Z')
yz_ = yz.quiver(0., 0., 0., 0., color="green",angles='xy', scale_units='xy', scale=1)

xz = fig.add_subplot(gs[1, 0])  # fig内部に軸を生成
xz.set_xlim(minmax)
xz.set_ylim(minmax)
xz.set_xlabel('X')
xz.set_ylabel('Z')
xz_ = xz.quiver(0., 0., 0., 0., color="red",angles='xy', scale_units='xy', scale=1)
# ------------------------- 図の設定 ------------------------- #
xyz = fig.add_subplot(gs[1, 1], projection='3d')  # fig内部に軸を生成
xyz.set_xlim(minmax)
xyz.set_ylim(minmax)
xyz.set_zlim(minmax)
xyz.set_xlabel('X')
xyz.set_ylabel('Y')
xyz.set_zlabel('Z')
# xyz_ = xyz.quiver(0., 0., 0., 0., 0., 0.)
xyzx_ = xyz.quiver(0., 0., 0., 0., 0., 0., color="blue")
xyzy_ = xyz.quiver(0., 0., 0., 0., 0., 0., color="green")
xyzz_ = xyz.quiver(0., 0., 0., 0., 0., 0., color="red")
# ------------------------- 計測し表示 ------------------------ #

# xyz.draw_artist(xyz.patch)
# xyz.draw_artist(line)

def getdata():
    global AHRS
    return AHRS.mag()

def xyplot(data):
    global Fusion
    global xy_
    xy_.set_UVC(data[0], data[1])


    # xy_.remove()
    # xy_ = xy.quiver(0, 0, data[0], data[1], color="blue",
    #                 angles='xy', scale_units='xy', scale=1)

def yzplot(data):
    global Fusion    
    global yz_
    yz_.set_UVC(data[1], data[2])    


    # yz_.remove()
    # yz_ = yz.quiver(0, 0, data[1], data[2], color="green",
    #                 angles='xy', scale_units='xy', scale=1)

def xzplot(data):
    global Fusion    
    global xz_
    xz_.set_UVC(data[0], data[2])

    # xz_.remove()
    # xz_ = xz.quiver(0, 0, data[0], data[2], color="red",
    #                 angles='xy', scale_units='xy', scale=1)

def xyzplot(data):
    global Fusion
    global xyzx_    
    global xyzy_    
    global xyzz_        

    xyzx_.set_segments([[[0,0,0],[data[0][0], data[0][1], data[0][2]]]])

    xyzy_.set_segments([[[0,0,0],[data[1][0], data[1][1], data[1][2]]]])

    xyzz_.set_segments([[[0,0,0],[data[2][0], data[2][1], data[2][2]]]])


    # xyzx_.remove()
    # xyzy_.remove()
    # xyzz_.remove()

    # data = Fusion.Rv([1, 0, 0])
    # xyzx_ = xyz.quiver(0, 0, 0, data[0], data[1], data[2], color="blue")

    # data = Fusion.Rv([0, 1, 0])
    # xyzy_ = xyz.quiver(0, 0, 0, data[0], data[1], data[2], color="green")

    # data = Fusion.Rv([0, 0, 1])
    # xyzz_ = xyz.quiver(0, 0, 0, data[0], data[1], data[2], color="red")

    # xyz.view_init(30, dt)
# -------------------------------------------------------- #
s = time()
t=s

q = [1, 0, 0, 0]#クォータニオン初期値（適当に）
theta = -54#磁場の角度
Fusion = fusion(q, theta)#重力や磁場の情報から姿勢を計算するfusionクラス
count = 0

from time import time, sleep
from openNetwork import *
# m=MediatorUDP(remote="192.168.0.115")
m=MediatorUDP(remote="10.0.1.4")
# m=MediatorUDP(remote="192.168.1.43")
sleep(1.)
m({"set":{"period":0.1}})
sleep(2.)
print("calibrate_gyro")
m({"calibrate_gyro":""})
sleep(5.)
print("calibrate_mag")
m({"calibrate_mag":5})
sleep(5)
period = 0.05
m({"set":{"period":period}})


while count < 5000:
    count += 1
    sleep(period/2.)
    plt.pause(0.001)
    try:
        # -------------------------------------------------------- #
        #                        姿勢計測試験                        #
        # -------------------------------------------------------- #
        if True:
            data = m()    
            print(data)
            accel = data["accel"]
            mag = data["mag"]
            gyro = data["gyro"]
            # print(accel,mag,gyro)
            # -------------------------------------------------------- #
            dt = time() - t
            # print(dt)
            # Fusion.updateMadwick(accel, mag, gyro, dt)
            # Fusion.update0(accel, mag, gyro, dt)
            # Fusion.update1(accel, mag, gyro, dt)
            Fusion.update20(accel, mag, gyro, dt)
            # Fusion.update__(accel, mag, gyro, dt)
            # Fusion.update_(accel, mag, gyro, dt)
            t = time()
            # -------------------------------------------------------- #
            # Fusion(accel, mag, gyro, dt)
            # data = accel
            # data = getdata()

            # print(["YPR", Fusion.YPR()])
            # print([dt,t])
            # fil([time()-s, data])
            # data = [time()-s, getdata()]
            # -------- 図を更新 ------- #
            # fig.suptitle(str(data))

            # sleep(0.01)
            xyplot(Fusion.Rv([1, 0, 0]))
            yzplot(Fusion.Rv([0, 1, 0]))
            xzplot(Fusion.Rv([0, 0, 1]))
            xyzplot([Fusion.Rv([1, 0, 0]),Fusion.Rv([0, 1, 0]),Fusion.Rv([0, 0, 1])])
        elif False:
           # -------------------------------------------------------- #
           #                        物体加速度計測試験                   #
           # -------------------------------------------------------- #
            data = m()    
            print(data)
            accel = data["accel"]
            mag = data["mag"]
            gyro = data["gyro"]
            # -------------------------------------------------------- #
            dt = time() - t
            Fusion.update20(accel, mag, gyro, dt)            
            t = time()
            a = Subtract(accel,Fusion.Rs([0.,0.,-1.]))
            a_elem = [Dot(a,[1,0,0]),Dot(a,[0,1,0]),Dot(a,[0,0,1])]
            xyplot(a_elem)
            yzplot(a_elem)
            xzplot(a_elem)            
            xyzplot([a_elem,a_elem,a_elem])                            
    except:
        pass
