# import smbus
try:
    from utime import sleep, time_ns
except:
    from time import sleep, time_ns
from math import atan2, pi
from .MPU6050 import MPU6050  # 同じディレクトリ内のファイルからクラスを読み取る方法
from .AK8963 import AK8963


##
# MPU9250には，履歴を保存するようにする
#
#

class MPU9250:

    def __init__(self, address_IN=0x68):
        self.address = address_IN
        self.MPU6050 = MPU6050(address_IN)
        self.AK8963 = AK8963(address_IN)

        self.history_length = 5
        t = time_ns()
        self.mag_history = [(t, (0, 0, 0))]*self.history_length
        self.gyro_history = [(t, (0, 0, 0))]*self.history_length
        self.accel_history = [(t, (0, 0, 0))]*self.history_length
        self.temp_history = [(t, 0)]*self.history_length
        print("\u001b[35m"+"MPU9250 is initialized"+"\u001b[0m")

    def mag(self):
        ret = self.AK8963.mag()
        # self.mag_history.insert(0, (time_ns(), ret))
        # self.mag_history.pop()

        return ret

    def accel(self):
        ret = self.MPU6050.accel()
        # self.accel_history.insert(0, (time_ns(), ret))
        # self.accel_history.pop()

        return ret

    def gyro(self):
        ret = self.MPU6050.gyro()
        # self.gyro_history.insert(0, (time_ns(), ret))
        # self.gyro_history.pop()

        return ret

    def __call__(self):
        return (self.MPU6050.accel(),
                self.AK8963.mag(),
                self.MPU6050.gyro())

    def AMG(self):
        return (self.MPU6050.accel(), self.AK8963.mag(), self.MPU6050.gyro())

    def temp(self):
        ret = self.MPU6050.temp()
        # self.temp_history.insert(0, (time_ns(), ret))
        # self.temp_history.pop()

        return ret
