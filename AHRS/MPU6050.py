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

from libi2c import *


class MPU6050:
    # some MPU6050 Registers and their Address
    PWR_MGMT_1 = 0x6B
    SMPLRT_DIV = 0x19
    CONFIG = 0x1A
    GYRO_CONFIG = 0x1B
    INT_ENABLE = 0x38
    #
    TEMP_OUT = 0x41
    ACCEL_XOUT = 0x3B
    ACCEL_YOUT = 0x3D
    ACCEL_ZOUT = 0x3F
    GYRO_XOUT = 0x43
    GYRO_YOUT = 0x45
    GYRO_ZOUT = 0x47

    def __init__(self, address_IN=0x68):

        if _MicroPython_:
            self.bus = I2C(scl=Pin(22), sda=Pin(21))
        else:
            self.bus = smbus.SMBus(1)

        self.address = address_IN
        #!このself.addressにwriteする関数を使っている
        # write to sample rate register
        write_byte_data(self.bus, self.address, self.SMPLRT_DIV, 7)
        # Write to power management register
        write_byte_data(self.bus, self.address, self.PWR_MGMT_1, 1)
        # Write to Configuration register
        write_byte_data(self.bus, self.address, self.CONFIG, 0)
        # Write to Gyro configuration register
        write_byte_data(self.bus, self.address, self.GYRO_CONFIG, 24)
        # Write to interrupt enable register
        write_byte_data(self.bus, self.address, self.INT_ENABLE, 1)
        self.is_gyro_calibrated = False
        self.is_accel_calibrated = False
        self.off_gyro = [0, 0, 0]
        zero4 = [0, 0, 0, 0]
        self.M = [zero4, zero4, zero4, zero4]
        print("\u001b[35m"+"MPU6050 is initialized"+"\u001b[0m")
    # -------------------------------------------------------- #

    def bytes2int(self, firstbyte, secondbyte):
        if _MicroPython_:
            # オーバーフローのチェック
            if not firstbyte & 0x80:
                return firstbyte << 8 | secondbyte
            return - (((firstbyte ^ 255) << 8) | (secondbyte ^ 255) + 1)
        else:
            value = (firstbyte << 8) + secondbyte
            if(value > 32768):
                value -= 65536
            return value

    def read_byte_data(self, register):
        if _MicroPython_:
            high, low = self.bus.readfrom_mem(self.address, register, 2)
            return self.bytes2int(high, low)
        else:
            high, low = self.bus.read_i2c_block_data(self.address, register, 2)
            return self.bytes2int(high, low)
    # -------------------------------------------------------- #

    def calibrate_gyro(self):
        print("\u001b[33m"+"start calibrating gyro"+"\u001b[0m")
        print("\u001b[33m"+"do not move the sensor"+"\u001b[0m")
        G = [0, 0, 0]
        for t in range(100):
            sleep(0.01)
            g = self.gyro()
            for i in range(3):
                G[i] += g[i]
        for i in range(3):
            G[i] /= 100
        self.off_gyro[0] += G[0]
        self.off_gyro[1] += G[1]
        self.off_gyro[2] += G[2]

        print("\n\u001b[33mcurrent offset = "+"\u001b[0m",
              self.off_gyro, "\n\u001b[33m"+"calibration done."+"\u001b[0m")

    def set_M(self, M):
        print("\u001b[34m"+"start calibrating accelerometer"+"\u001b[0m")
        self.M = M
        self.is_accel_calibrated = True
        print(self.M)

    def temp(self):
        temp = self.read_byte_data(self.TEMP_OUT)
        return temp / 340 + 36.53      # data sheet(register map)記載の計算式.

    def gyro(self):
        """
        物体が，各軸に対して時計回りに回転する角速度        
        便宜上符号を変えた
        """
        return (- self.read_byte_data(self.GYRO_XOUT) / 131.0 - self.off_gyro[0],
                - self.read_byte_data(self.GYRO_YOUT) /
                131.0 - self.off_gyro[1],
                - self.read_byte_data(self.GYRO_ZOUT) / 131.0 - self.off_gyro[2])
    # def accel(self):
    #     if self.is_accel_calibrated:
    #         return Dot(self.M,
    #                    [- self.read_byte_data(self.ACCEL_XOUT) / 16384.0,
    #                     - self.read_byte_data(self.ACCEL_YOUT) / 16384.0,
    #                     - self.read_byte_data(self.ACCEL_ZOUT) / 16384.0,
    #                     1.])
    #     else:
    #         return [
    #             - self.read_byte_data(self.ACCEL_XOUT) / 16384.0,
    #             - self.read_byte_data(self.ACCEL_YOUT) / 16384.0,
    #             - self.read_byte_data(self.ACCEL_ZOUT) / 16384.0
    #         ]

    def accel(self):
        return (- self.read_byte_data(self.ACCEL_XOUT) / 16384.0,
                - self.read_byte_data(self.ACCEL_YOUT) / 16384.0,
                - self.read_byte_data(self.ACCEL_ZOUT) / 16384.0)
