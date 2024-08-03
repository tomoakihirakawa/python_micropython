'''DOC_EXTRACT

# MPU9250



'''

import smbus
import time

class MPU9250:
    MPU9250_ADDRESS = 0x68
    AK8963_ADDRESS = 0x0C

    PWR_MGMT_1 = 0x6B
    CONFIG = 0x1A
    GYRO_CONFIG = 0x1B
    ACCEL_CONFIG = 0x1C
    ACCEL_CONFIG_2 = 0x1D
    INT_PIN_CFG = 0x37
    ACCEL_XOUT_H = 0x3B
    GYRO_XOUT_H = 0x43

    AK8963_ST1 = 0x02
    AK8963_XOUT_L = 0x03
    AK8963_XOUT_H = 0x04
    AK8963_YOUT_L = 0x05
    AK8963_YOUT_H = 0x06
    AK8963_ZOUT_L = 0x07
    AK8963_ZOUT_H = 0x08
    AK8963_ST2 = 0x09
    AK8963_CNTL1 = 0x0A
    AK8963_CNTL2 = 0x0B
    AK8963_ASAX = 0x10

    ACCEL_SCALE = 16384.0
    GYRO_SCALE = 131.0
    MAG_SCALE = 0.15

    def __init__(self, bus_num=1):
        self.bus = smbus.SMBus(bus_num)
        self.scale_x, self.scale_y, self.scale_z = self.mpu9250_init()

    def mpu9250_init(self):
        try:
            self.bus.write_byte_data(self.MPU9250_ADDRESS, self.PWR_MGMT_1, 0x00)
            time.sleep(0.1)

            self.bus.write_byte_data(self.MPU9250_ADDRESS, self.CONFIG, 0x01)
            self.bus.write_byte_data(self.MPU9250_ADDRESS, self.GYRO_CONFIG, 0x00)
            self.bus.write_byte_data(self.MPU9250_ADDRESS, self.ACCEL_CONFIG, 0x00)
            self.bus.write_byte_data(self.MPU9250_ADDRESS, self.ACCEL_CONFIG_2, 0x01)

            self.bus.write_byte_data(self.MPU9250_ADDRESS, self.INT_PIN_CFG, 0x02)
            time.sleep(0.1)

            self.bus.write_byte_data(self.AK8963_ADDRESS, self.AK8963_CNTL2, 0x01)
            time.sleep(0.1)

            self.bus.write_byte_data(self.AK8963_ADDRESS, self.AK8963_CNTL1, 0x16)
            time.sleep(0.1)

            scale_data = self.bus.read_i2c_block_data(self.AK8963_ADDRESS, self.AK8963_ASAX, 3)
            scale_x = (scale_data[0] - 128) / 256.0 + 1.0
            scale_y = (scale_data[1] - 128) / 256.0 + 1.0
            scale_z = (scale_data[2] - 128) / 256.0 + 1.0

            return scale_x, scale_y, scale_z
        except OSError as e:
            print(f"Error initializing MPU9250: {e}")
            return 1.0, 1.0, 1.0

    def read_raw_data(self, addr):
        try:
            high = self.bus.read_byte_data(self.MPU9250_ADDRESS, addr)
            low = self.bus.read_byte_data(self.MPU9250_ADDRESS, addr + 1)
            value = (high << 8) | low
            if value > 32768:
                value = value - 65536
            return value
        except OSError as e:
            print(f"Error reading raw data from MPU9250: {e}")
            return 0

    def read_raw_data_ak8963(self, addr):
        try:
            low = self.bus.read_byte_data(self.AK8963_ADDRESS, addr)
            high = self.bus.read_byte_data(self.AK8963_ADDRESS, addr + 1)
            value = (high << 8) | low
            if value > 32768:
                value = value - 65536
            return value
        except OSError as e:
            print(f"Error reading raw data from AK8963: {e}")
            return 0

    def read_accel_data(self):
        accel_x = self.read_raw_data(self.ACCEL_XOUT_H) / self.ACCEL_SCALE
        accel_y = self.read_raw_data(self.ACCEL_XOUT_H + 2) / self.ACCEL_SCALE
        accel_z = self.read_raw_data(self.ACCEL_XOUT_H + 4) / self.ACCEL_SCALE
        return accel_x, accel_y, accel_z

    def read_gyro_data(self):
        gyro_x = self.read_raw_data(self.GYRO_XOUT_H) / self.GYRO_SCALE
        gyro_y = self.read_raw_data(self.GYRO_XOUT_H + 2) / self.GYRO_SCALE
        gyro_z = self.read_raw_data(self.GYRO_XOUT_H + 4) / self.GYRO_SCALE
        return gyro_x, gyro_y, gyro_z

    def read_mag_data(self):
        try:
            self.bus.read_byte_data(self.AK8963_ADDRESS, self.AK8963_ST1)
            mag_x = self.read_raw_data_ak8963(self.AK8963_XOUT_L) * self.MAG_SCALE * self.scale_x
            mag_y = self.read_raw_data_ak8963(self.AK8963_YOUT_L) * self.MAG_SCALE * self.scale_y
            mag_z = self.read_raw_data_ak8963(self.AK8963_ZOUT_L) * self.MAG_SCALE * self.scale_z
            self.bus.read_byte_data(self.AK8963_ADDRESS, self.AK8963_ST2)
            return mag_x, mag_y, mag_z
        except OSError as e:
            print(f"Error reading mag data: {e}")
            return 0, 0, 0

def main():
    mpu = MPU9250()
    with open("data.csv", "w") as file:
        file.write("time, ax, ay, az, gx, gy, gz, mx, my, mz\n")
        start = time.time()

        while True:
            accel_x, accel_y, accel_z = mpu.read_accel_data()
            gyro_x, gyro_y, gyro_z = mpu.read_gyro_data()
            mag_x, mag_y, mag_z = mpu.read_mag_data()

            print(f"Accel X: {accel_x:.2f} g, Accel Y: {accel_y:.2f} g, Accel Z: {accel_z:.2f} g")
            print(f"Gyro X: {gyro_x:.2f} deg/s, Gyro Y: {gyro_y:.2f} deg/s, Gyro Z: {gyro_z:.2f} deg/s")
            print(f"Mag X: {mag_x:.2f} μT, Mag Y: {mag_y:.2f} μT, Mag Z: {mag_z:.2f} μT")

            file.write(f"{time.time() - start:.2f}, {accel_x:.2f}, {accel_y:.2f}, {accel_z:.2f}, {gyro_x:.2f}, {gyro_y:.2f}, {gyro_z:.2f}, {mag_x:.2f}, {mag_y:.2f}, {mag_z:.2f}\n")

            time.sleep(0.02)

            if time.time() - start > 50:
                break

if __name__ == "__main__":
    main()