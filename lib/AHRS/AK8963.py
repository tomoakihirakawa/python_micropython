# 参考ページ
# https://qiita.com/boyaki_machine/items/915f7730c737f2a5cc79

try:
    # microptyhonの場合
    from machine import SoftI2C as I2C
    from machine import Pin
    import ustruct as struct
    from utime import sleep
    _MicroPython_ = True
except:
    # ラズパイの場合
    try:
        import smbus
        from time import sleep
        _MicroPython_ = False

    except:
        print("\u001b[35m")
        print('please install smbus')
        print("\u001b[0m")

from ..libi2c import *
# -------------------------------------------------------- #

import time
from math import atan2, pi


class AK8963:
    """
    AK8963を利用するためのクラス    
    Register Table
    Name 	Address 	READ/WRITE      Description         Bit width
    # --------------------------------------------------------------------- #
    HXL 	03H 	    READ            Measurement data    8           X-axis data
    HXH 	04H                                         	8			                        
    HYL 	05H                                             8           Y-axis data 		                        
    HYH 	06H                                             8 
    HZL 	07H                                             8           Z-axis data 		                        
    HZH 	08H                                             8
    ST2     09H         READ            Status 2            8           Data status    
    """
    # AK8963 registers
    AK8963_ST1 = 0x02
    REG_INT_PIN_CFG = 0x37
    REG_PWR_MGMT_1 = 0x6B
    HXH = 0x04
    HYH = 0x06
    HZH = 0x08
    AK8963_ST2 = 0x09
    AK8963_CNTL = 0x0A
    mag_sens = 4900.0  # magnetometer sensitivity: 4800 uT

    def __init__(self, address_IN=0x68):

        # -------------------------------------------------------- #
        if _MicroPython_:
            self.bus = I2C(scl=Pin(22), sda=Pin(21))
        else:
            self.bus = smbus.SMBus(1)
        # -------------------------------------------------------- #

        self.address = address_IN
        self.addrAK8963 = 0x0C
        self._offset = [0, 0, 0]
        self._scale = [1, 1, 1]
        # I2Cで磁気センサ機能(AK8963)へアクセスできるようにする(BYPASS_EN=1)
        write_byte_data(self.bus, address_IN, self.REG_INT_PIN_CFG, 0x02)
        time.sleep(0.005)

        write_byte_data(self.bus, self.addrAK8963, self.AK8963_CNTL, 0x00)
        time.sleep(0.005)
        ##### モードの設定 #####
        AK8963_bit_res = 0x10  # 0b0001 = 16-bit 0x10
        #### 測定モードの設定 #####
        # AK8963_mode = 0x02  # 8 Hz連続測定モード１(0b0110)
        AK8963_mode = 0x06  # 100 Hz連続測定モード２(0b0010)
        # AK8963_mode = 0x00  # パワーダウンモード
        # AK8963_mode = 0x04  # 外部トリガ測定モード
        # AK8963_mode = 0x08  # セルフテストモード

        # (mode | output) (計測モード|センサーの出力方式) をself.AK8963_CNTLに入力
        write_byte_data(self.bus, self.addrAK8963, self.AK8963_CNTL,
                        (AK8963_mode | AK8963_bit_res))  # hexでないとビット演算にならない
        time.sleep(0.005)

        self.is_calibrated = False
        self.M = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]

        print("\u001b[35m"+"AK8963 is initialized"+"\u001b[0m")

    def set_M(self, M):
        self.M = M
        self.is_calibrated = True
        print(self.M)

    def calibrate(self, time_span):
        print("\u001b[33m"+"calibrating, time = " +
              str(time_span) + "\u001b[0m")
        s = time.time()
        M = [0, 0, 0]
        minmaxM = [[10**10, -10**10], [10**10, -10**10], [10**10, -10**10]]
        while((time.time()-s) < time_span):
            time.sleep(0.02)
            M = self.mag()
            print(M)
            for i in range(3):  # x,y,z
                if(minmaxM[i][0] > M[i]):
                    minmaxM[i][0] = M[i]
                if(minmaxM[i][1] < M[i]):
                    minmaxM[i][1] = M[i]

        newoffset = [(minmaxM[0][1] + minmaxM[0][0])/2,
                     (minmaxM[1][1] + minmaxM[1][0])/2,
                     (minmaxM[2][1] + minmaxM[2][0])/2]

        self.setOffset(newoffset)

        # Soft iron correction
        avg_delta_x = (minmaxM[0][1] - minmaxM[0][0])/2
        avg_delta_y = (minmaxM[1][1] - minmaxM[1][0])/2
        avg_delta_z = (minmaxM[2][1] - minmaxM[2][0])/2
        avg_delta = (avg_delta_x + avg_delta_y + avg_delta_z) / 3
        scale_x = avg_delta / avg_delta_x
        scale_y = avg_delta / avg_delta_y
        scale_z = avg_delta / avg_delta_z
        self._scale = [scale_x, scale_y, scale_z]

        print("\n\u001b[33mnewoffset = ", newoffset, "\u001b[0m")
        print("\n\u001b[33mcurrent offset = "+"\u001b[0m",
              self._offset, "\n\u001b[33m"+"calibration done."+"\u001b[0m")

    def calibrate_visually(self, time_span):
        """
        図で確かめながら校正する
        """
        import matplotlib.pyplot as plt
        print("\u001b[33m"+"calibrating, time = "+str(time_span) + "\u001b[0m")
        s = time.time()
        # ------------------------- 図 ------------------------- #
        fig = plt.figure()  # 図を生成
        ax3d = fig.add_subplot(111, projection='3d')  # fig内部に軸を生成
        r = [-3., 3.]  # range
        ax3d.set_xlim(r)
        ax3d.set_ylim(r)
        ax3d.set_zlim(r)
        sc = ax3d.scatter([0.], [0.], [0.])
        data = [[], [], []]
        while((time.time()-s) < time_span):
            mag = self.mag()
            data[0].append(mag[0])  # 図用にmagにデータを蓄積
            data[1].append(mag[1])  # 図用にmagにデータを蓄積
            data[2].append(mag[2])  # 図用にmagにデータを蓄積
            sc._offsets3d = (data[0], data[1], data[2])
            ax3d.view_init(30, time.time()-s)
            plt.pause(0.01)
        # -------------------------------------------------------- #
        newoffset = [(max(data[0]) + min(data[0]))/2,
                     (max(data[1]) + min(data[1]))/2,
                     (max(data[2]) + min(data[2]))/2]

        # hard iron correction
        self.setOffset(newoffset)

        # soft iron correction
        avg_delta_x = (max(data[0]) - min(data[0]))/2
        avg_delta_y = (max(data[1]) - min(data[1]))/2
        avg_delta_z = (max(data[2]) - min(data[2]))/2
        avg_delta = (avg_delta_x + avg_delta_y + avg_delta_z) / 3
        scale_x = avg_delta / avg_delta_x
        scale_y = avg_delta / avg_delta_y
        scale_z = avg_delta / avg_delta_z
        newscale = [scale_x, scale_y, scale_z]
        self.setScale(newscale)

        print("\n\u001b[33mnewoffset = ", newoffset, "\u001b[0m")
        print("\n\u001b[33mnewscale = ", newscale, "\u001b[0m")
        print("\n\u001b[33mcurrent offset = "+"\u001b[0m",
              self._offset, "\n\u001b[33m"+"calibration done."+"\u001b[0m")
        plt.pause(1.)

    def setOffset(self, offIN):
        self._offset[0] += offIN[0]
        self._offset[1] += offIN[1]
        self._offset[2] += offIN[2]

    def setScale(self, scale):
        self._scale[0] *= scale[0]
        self._scale[1] *= scale[0]
        self._scale[2] *= scale[0]

    def mag(self):
        status = read_byte_data(self.bus, self.addrAK8963, self.AK8963_ST1, 1)
        while (status[0] & 0x01) != 0x01:
            # データレディ状態まで待つ
            time.sleep(0.002)
            status = read_byte_data(
                self.bus, self.addrAK8963, self.AK8963_ST1, 1)

        # データ読み出し．データシートを確認
        hxl, hxh, hyl, hyh, hzl, hzh, st2 = read_byte_data(
            self.bus, self.addrAK8963, 0x03, 7)

        # 0x03,0x04,0x05,0x06,0x07,0x08,0x09 -> 7byte
        rawX = (hxh << 8 | hxl)  # 下位bitが先
        rawY = (hyh << 8 | hyl)  # 下位bitが先
        rawZ = (hzh << 8 | hzl)  # 下位bitが先

        # オーバーフローチェック
        if (st2 & 0x08) == 0x08:  # highならオーバーフロー
            # オーバーフローのため正しい値が得られていない
            print(hxl, hxh, hyl, hyh, hzl, hzh, st2)
            raise Exception('004 Mag sensor over flow')

        if(rawX > 32768):
            rawX -= 65536
        if(rawY > 32768):
            rawY -= 65536
        if(rawZ > 32768):
            rawZ -= 65536

        # return rawX/32768*4.9/1000, rawY/32768*4.9/1000, rawZ/32768*4.9/1000

        # micro 10^-5
        # return [rawX/32768*490.-self._offset[0], rawY/32768*490.-self._offset[1], rawZ/32768*490.-self._offset[2]]

        # return rawX/32768*4.9, rawY/32768*4.9, rawZ/32768*4.9#milli 10^-3
        # return rawX/32768*4900.-self._offset[0], rawY/32768*4900.-self._offset[1], rawZ/32768*4900.-self._offset[2]  # micro 10^-6
        # return rawX/32768*4900.*1000, rawY/32768*4900.*1000, rawZ/32768*4900.*1000  # nano 10^-9

        """
        
        original coordinate of AK8963 in MPU9250
        
           +X
        +------+
        |*     |  -> +Y
        |  -Z  |
        +------+
        +------+
           +Z        

        change this coordinate
        
           +Y
        +------+
        |*     |  -> +X
        |  +Z  |
        +------+
        +------+
           -Z        

        """

        # tmp = [rawY/32768*490., rawX/32768*490., -rawZ/32768*490.]

        # tmp[0] -= self._offset[0]
        # tmp[1] -= self._offset[1]
        # tmp[2] -= self._offset[2]

        # tmp[0] *= self._scale[0]
        # tmp[1] *= self._scale[1]
        # tmp[2] *= self._scale[2]

        # タプルに変更した
        return ((rawY/32768*490. - self._offset[0])*self._scale[0],
                (rawX/32768*490. - self._offset[1])*self._scale[1],
                (-rawZ/32768*490. - self._offset[2])*self._scale[2])
