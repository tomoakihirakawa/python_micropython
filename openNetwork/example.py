from ServerUDP import *

## -------------------------------------------------------- #
##                            例２                           #
## -------------------------------------------------------- #
#! -------------------------------------------------------- #
#!                           多重継承                        #
#! -------------------------------------------------------- #
try:
    # micropythonの場合つかえる
    from imu import mpu9250

    class IMUServer(mpu9250, ServerUDP):

        DATA = {}

        def __init__(self, ssid=None, password=None):
            ServerUDP.__init__(self, ssid=ssid, password=password)
            mpu9250.__init__(self)

            _thread.start_new_thread(self.update, ())

        def update(self):
            while True:
                sleep(0.05)
                self.DATA = {'m': mpu9250.mag(self),
                             'a': mpu9250.accel(self),
                             'w': mpu9250.gyro(self),
                             't': time_ns()}

        def functions(self, key):
            if key == 'DATA':
                return self.DATA
            else:
                return "None"
except:
    pass

# -------------------------------------------------------- #


def example():
    # ssid = 'TH15'
    # password = '8ry37sc2'
    # s = DummySensorServer(ssid,password)

    # ssid = 'TimeCapsule'
    # password = 'Tomoaki813;'
    # s = IMUServer(ssid,password)
    # s.start()

    s = DummySensorServer()
    s.start()

if __name__ == '__main__':
    example()


"""
このプログラムを直接走らせると，
ローカルサーバーが走り出す．

それに続いて，
m=mediaterクラスを別ターミナルで作成し，
m.get('m')などとすると，データが帰ってくる．
"""