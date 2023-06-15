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


class WT901:
    # IIC address of the module, default is 0x50. IIC address
    # some WT901 Registers and their Address
    # RegAddr Symbol Meaning
    SAVE = 0x00  # Save
    CALSW = 0x01  # Calibration
    RSW = 0x02  # Return data content
    RATE = 0x03  # Return data Speed
    BAUD = 0x04  # Baud rate
    AXOFFSET = 0x05  # X axis Acceleration bias
    AYOFFSET = 0x06  # Y axis Acceleration bias
    AZOFFSET = 0x07  # Z axis Acceleration bias
    GXOFFSET = 0x08  # X axis angular velocity bias
    GYOFFSET = 0x09  # Y axis angular velocity bias
    GZOFFSET = 0x0a  # Z axis angular velocity bias
    HXOFFSET = 0x0b  # X axis Magnetic bias
    HYOFFSET = 0x0c  # Y axis Magnetic bias
    HZOFFSET = 0x0d  # Z axis Magnetic bias
    D0MODE = 0x0e  # D0 mode
    D1MODE = 0x0f  # D1 mode
    D2MODE = 0x10  # D2 mode
    D3MODE = 0x11  # D3 mode
    D0PWMH = 0x12  # D0PWM High-level width
    D1PWMH = 0x13  # D1PWM High-level width
    D2PWMH = 0x14  # D2PWM High-level width
    D3PWMH = 0x15  # D3PWM High-level width
    D0PWMT = 0x16  # D0PWM Period
    D1PWMT = 0x17  # D1PWM Period
    D2PWMT = 0x18  # D2PWM Period
    D3PWMT = 0x19  # D3PWM Period
    IICADDR = 0x1a  # IIC address
    LEDOFF = 0x1b  # Turn off LED
    GPSBAUD = 0x1c  # GPS baud rate
    MMYY = 0x30  # Month , Year
    HHDD = 0x31  # Hour , Day
    SSMM = 0x32  # Second , Minute
    MS = 0x33  # Millisecond
    AX = 0x34  # X axis Acceleration
    AY = 0x35  # Y axis Acceleration
    AZ = 0x36  # Z axis Acceleration
    GX = 0x37  # X axis angular velocity
    GY = 0x38  # Y axis angular velocity
    GZ = 0x39  # Z axis angular velocity
    HX = 0x3a  # X axis Magnetic
    HY = 0x3b  # Y axis Magnetic
    HZ = 0x3c  # Z axis Magnetic
    Roll = 0x3d  # X axis Angle
    Pitch = 0x3e  # Y axis Angle
    Yaw = 0x3f  # Z axis Angle
    TEMP = 0x40  # Temperature
    D0Status = 0x41  # D0Status
    D1Status = 0x42  # D1Status
    D2Status = 0x43  # D2Status
    D3Status = 0x44  # D3Status
    PressureL = 0x45  # Pressure Low Byte
    PressureH = 0x46  # Pressure High Byte
    HeightL = 0x47  # Height Low Byte
    HeightH = 0x48  # Height High Byte
    LonL = 0x49  # Longitude Low Byte
    LonH = 0x4a  # Longitude High Byte
    LatL = 0x4b  # Latitude Low Byte
    LatH = 0x4c  # Latitude High Byte
    GPSHeight = 0x4d  # GPS Height
    GPSYaw = 0x4e  # GPS Yaw
    GPSVL = 0x4f  # GPS speed Low byte
    GPSVH = 0x50  # GPS speed High byte
    Q0 = 0x51  # Quaternion Q0
    Q1 = 0x52  # Quaternion Q1
    Q2 = 0x53  # Quaternion Q2
    Q3 = 0x54  # Quaternion Q3

    # PWR_MGMT_1 = 0x6B
    # SMPLRT_DIV = 0x19
    # CONFIG = 0x1A
    # GYRO_CONFIG = 0x1B
    # INT_ENABLE = 0x38
    # #
    # TEMP_OUT = 0x41
    # ACCEL_XOUT = 0x3B
    # ACCEL_YOUT = 0x3D
    # ACCEL_ZOUT = 0x3F
    # GYRO_XOUT = 0x43
    # GYRO_YOUT = 0x45
    # GYRO_ZOUT = 0x47

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
