import gpiod
import smbus2
import time

# Constants for the VL53L0X
I2C_ADDRESS = 0x29  # Default I2C address for VL53L0X
REG_SYSRANGE_START = 0x00

# Create an instance of the I2C bus
bus = smbus2.SMBus(1)  # 1 indicates /dev/i2c-1

# GPIO setup
try:
    chip = gpiod.Chip('gpiochip0')  # Check your GPIO chip number
    xshut = chip.get_line(5)  # Replace with your XSHUT GPIO pin number

    # Requesting lines
    xshut.request(consumer='vl53l0x_xshut', type=gpiod.LINE_REQ_DIR_OUT)
except Exception as e:
    print(f"Error setting up GPIO: {e}")
    exit(1)

def write_byte_data(addr, reg, data):
    bus.write_byte_data(addr, reg, data)

def read_byte_data(addr, reg):
    return bus.read_byte_data(addr, reg)

def read_block_data(addr, reg, length):
    return bus.read_i2c_block_data(addr, reg, length)

def init_sensor():
    # Initialize the VL53L0X sensor
    try:
        xshut.set_value(1)
        time.sleep(0.1)  # Give some time to power up

        # You can add more initialization sequences here
        write_byte_data(I2C_ADDRESS, 0x80, 0x01)
        write_byte_data(I2C_ADDRESS, 0xFF, 0x01)
        write_byte_data(I2C_ADDRESS, 0x00, 0x00)
        # Initialize other required registers as per datasheet
        
    except Exception as e:
        print(f"Error initializing VL53L0X sensor: {e}")

def measure_distance():
    try:
        # Start a measurement
        write_byte_data(I2C_ADDRESS, REG_SYSRANGE_START, 0x01)
        time.sleep(0.05)  # Wait for the measurement to complete

        # Read the range in millimeters
        range_mm = read_byte_data(I2C_ADDRESS, 0x1E)
        return range_mm
    except Exception as e:
        print(f"Error measuring distance: {e}")
        return None

try:
    init_sensor()
    while True:
        distance = measure_distance()
        if distance is not None:
            print(f"Distance: {distance} mm")
        time.sleep(1)

except KeyboardInterrupt:
    print("Measurement stopped by user")

finally:
    try:
        xshut.set_value(0)
        xshut.release()
        chip.close()
    except Exception as e:
        print(f"Error releasing GPIO resources: {e}")
