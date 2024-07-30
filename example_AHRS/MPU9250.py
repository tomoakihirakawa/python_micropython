import smbus
import time

# MPU9250のI2Cアドレス
MPU9250_ADDRESS = 0x68
AK8963_ADDRESS = 0x0C

# MPU9250レジスタアドレス
PWR_MGMT_1 = 0x6B
CONFIG = 0x1A
GYRO_CONFIG = 0x1B
ACCEL_CONFIG = 0x1C
ACCEL_CONFIG_2 = 0x1D
INT_PIN_CFG = 0x37
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43

# AK8963レジスタアドレス
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

# I2Cバス番号
bus = smbus.SMBus(1)

# スケーリング定数
ACCEL_SCALE = 16384.0  # 加速度計のスケーリング定数（2G範囲）
GYRO_SCALE = 131.0     # ジャイロスコープのスケーリング定数（250deg/s範囲）
MAG_SCALE = 0.15       # 磁力計のスケーリング定数（データシートに基づく）

# MPU9250の初期化
def mpu9250_init():
    try:
        # MPU9250をスリープから解除
        bus.write_byte_data(MPU9250_ADDRESS, PWR_MGMT_1, 0x00)
        time.sleep(0.1)
        
        # コンフィギュレーション
        bus.write_byte_data(MPU9250_ADDRESS, CONFIG, 0x01)
        bus.write_byte_data(MPU9250_ADDRESS, GYRO_CONFIG, 0x00)
        bus.write_byte_data(MPU9250_ADDRESS, ACCEL_CONFIG, 0x00)
        bus.write_byte_data(MPU9250_ADDRESS, ACCEL_CONFIG_2, 0x01)
        
        # バイパスモード設定
        bus.write_byte_data(MPU9250_ADDRESS, INT_PIN_CFG, 0x02)
        time.sleep(0.1)
        
        # 磁力計をリセット
        bus.write_byte_data(AK8963_ADDRESS, AK8963_CNTL2, 0x01)
        time.sleep(0.1)
        
        # 磁力計を連続測定モード2に設定
        bus.write_byte_data(AK8963_ADDRESS, AK8963_CNTL1, 0x16)
        time.sleep(0.1)
        
        # 磁力計キャリブレーションデータの読み取り
        scale_data = bus.read_i2c_block_data(AK8963_ADDRESS, AK8963_ASAX, 3)
        scale_x = (scale_data[0] - 128) / 256.0 + 1.0
        scale_y = (scale_data[1] - 128) / 256.0 + 1.0
        scale_z = (scale_data[2] - 128) / 256.0 + 1.0
        
        return scale_x, scale_y, scale_z
    except OSError as e:
        print(f"Error initializing MPU9250: {e}")
        return 1.0, 1.0, 1.0

# 16ビットの値を読み取る関数
def read_raw_data(addr):
    try:
        high = bus.read_byte_data(MPU9250_ADDRESS, addr)
        low = bus.read_byte_data(MPU9250_ADDRESS, addr + 1)
        value = (high << 8) | low
        if value > 32768:
            value = value - 65536
        return value
    except OSError as e:
        print(f"Error reading raw data from MPU9250: {e}")
        return 0

# 磁力計のデータを読み取る関数
def read_mag_data(scale_x, scale_y, scale_z):
    try:
        bus.read_byte_data(AK8963_ADDRESS, AK8963_ST1)  # Status register to initiate the read
        mag_x = read_raw_data_ak8963(AK8963_XOUT_L) * scale_x
        mag_y = read_raw_data_ak8963(AK8963_YOUT_L) * scale_y
        mag_z = read_raw_data_ak8963(AK8963_ZOUT_L) * scale_z
        bus.read_byte_data(AK8963_ADDRESS, AK8963_ST2)  # Read ST2 to clear the data register
        return mag_x, mag_y, mag_z
    except OSError as e:
        print(f"Error reading mag data: {e}")
        return 0, 0, 0

# AK8963から16ビットの値を読み取る関数
def read_raw_data_ak8963(addr):
    try:
        low = bus.read_byte_data(AK8963_ADDRESS, addr)
        high = bus.read_byte_data(AK8963_ADDRESS, addr + 1)
        value = (high << 8) | low
        if value > 32768:
            value = value - 65536
        return value
    except OSError as e:
        print(f"Error reading raw data from AK8963: {e}")
        return 0

# メインループ
def main():
    scale_x, scale_y, scale_z = mpu9250_init()
    with open("data.csv", "w") as file:
        file.write("time, ax, ay, az, gx, gy, gz, mx, my, mz\n")
        start = time.time()

        while True:
            # 加速度データの読み取り
            accel_x = read_raw_data(ACCEL_XOUT_H) / ACCEL_SCALE
            accel_y = read_raw_data(ACCEL_XOUT_H + 2) / ACCEL_SCALE
            accel_z = read_raw_data(ACCEL_XOUT_H + 4) / ACCEL_SCALE
            
            # ジャイロデータの読み取り
            gyro_x = read_raw_data(GYRO_XOUT_H) / GYRO_SCALE
            gyro_y = read_raw_data(GYRO_XOUT_H + 2) / GYRO_SCALE
            gyro_z = read_raw_data(GYRO_XOUT_H + 4) / GYRO_SCALE
            
            # 磁力計データの読み取り
            mag_x, mag_y, mag_z = read_mag_data(scale_x, scale_y, scale_z)
            mag_x *= MAG_SCALE
            mag_y *= MAG_SCALE
            mag_z *= MAG_SCALE
            
            # 取得したデータを表示
            print(f"Accel X: {accel_x:.2f} g, Accel Y: {accel_y:.2f} g, Accel Z: {accel_z:.2f} g")
            print(f"Gyro X: {gyro_x:.2f} deg/s, Gyro Y: {gyro_y:.2f} deg/s, Gyro Z: {gyro_z:.2f} deg/s")
            print(f"Mag X: {mag_x:.2f} μT, Mag Y: {mag_y:.2f} μT, Mag Z: {mag_z:.2f} μT")

            # ファイルにデータを書き込む
            file.write(f"{time.time() - start:.2f}, {accel_x:.2f}, {accel_y:.2f}, {accel_z:.2f}, {gyro_x:.2f}, {gyro_y:.2f}, {gyro_z:.2f}, {mag_x:.2f}, {mag_y:.2f}, {mag_z:.2f}\n")

            # 0.1秒待機
            time.sleep(0.02)

            # 10秒経過したら終了
            if time.time() - start > 50:
                break

if __name__ == "__main__":
    main()
