'''DOC_EXTRACT

I2Cバス１のアドレス0x29に接続されていることを確認します．

```sh
i2cdetect -y 1
```

```sh
pi@pi:~/research/ToF_sensor $ i2cdetect -y 1
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- 29 -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- --     
```

`I2C_ADDRESS`に，16進数でこのアドレスを指定しておきます．

```python
I2C_ADDRESS = 0x29
```

'''

import smbus2
import time
from gpiozero import DigitalOutputDevice

# Constants for the VL53L0X
I2C_ADDRESS = 0x29  # Default I2C address for VL53L0X

# Setup GPIO for XSHUT control using gpiozero
try:
    xshut = DigitalOutputDevice(20)  # GPIO17 (BCM numbering)
except Exception as e:
    print(f"Error initializing GPIO20: {e}")
    exit(1)

# Create an instance of the I2C bus
bus = smbus2.SMBus(1)  # 1 indicates /dev/i2c-1

def write_byte_data(addr, reg, data):
    bus.write_byte_data(addr, reg, data)

def read_byte_data(addr, reg):
    return bus.read_byte_data(addr, reg)

def init_sensor():
    try:
        # Reset the sensor using XSHUT
        xshut.off()  # Set XSHUT to low
        time.sleep(0.1)
        xshut.on()  # Set XSHUT to high
        time.sleep(0.1)  # Give some time to power up

        # Sensor initialization sequence
        write_byte_data(I2C_ADDRESS, 0x88, 0x00)
        write_byte_data(I2C_ADDRESS, 0x80, 0x01)
        write_byte_data(I2C_ADDRESS, 0xFF, 0x01)
        write_byte_data(I2C_ADDRESS, 0x00, 0x00)
        write_byte_data(I2C_ADDRESS, 0x91, 0x3C)
        write_byte_data(I2C_ADDRESS, 0x00, 0x01)
        write_byte_data(I2C_ADDRESS, 0xFF, 0x00)
        write_byte_data(I2C_ADDRESS, 0x80, 0x00)

    except Exception as e:
        print(f"Error initializing VL53L0X sensor: {e}")

def measure_distance():
    try:
        write_byte_data(I2C_ADDRESS, 0x00, 0x01)  # Start measurement
        time.sleep(0.02)  # Wait for the measurement to complete (20 ms)

        range_status = read_byte_data(I2C_ADDRESS, 0x14)
        if (range_status & 0x01) == 0:  # Check if the measurement is ready
            range_mm = (read_byte_data(I2C_ADDRESS, 0x14 + 10) << 8) + read_byte_data(I2C_ADDRESS, 0x14 + 11)
            return range_mm
    except Exception as e:
        print(f"Error measuring distance: {e}")
        return None

try:
    init_sensor()
    while True:
        distance = measure_distance()
        if distance is not None:
            print(f"Distance: {distance} mm", "-"*(int(distance/10)))
            time.sleep(0.02)  # 20 ms delay for high speed mode
except KeyboardInterrupt:
    print("Measurement stopped by user")
finally:
    if xshut:
        xshut.off()  # Ensure XSHUT is turned off when done