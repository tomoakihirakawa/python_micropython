
_black_ = "\u001b[30m"
_red_ = "\u001b[31m"
_green_ = "\u001b[32m"
_yellow_ = "\u001b[33m"
_blue_ = "\u001b[34m"
_magenta_ = "\u001b[35m"
_cyan_ = "\u001b[36m"
_white_ = "\u001b[37m"
_default_color_ = "\u001b[0m"


try:
    from .MS5837 import MS5837_02BA
    print(_green_+" * pressureSensors.MS5837.MS5837_02BA"+_default_color_)
except:
    print(_red_+" x pressureSensors.MS5837"+_default_color_)

try:
    from .MS5837 import MS5837_30BA
    print(_green_+" * pressureSensors.MS5837.MS5837_30BA"+_default_color_)
except:
    print(_red_+" x pressureSensors.MS5837"+_default_color_)


# これによってimu.mpu6050としてmpu6050.mpu6050がつかえるようになる
print("\u001b[35m")
print("pressureSensors is imported")
print("You can use:")
print(" * pressureSensors.MS5837_02BA")
print(" * pressureSensors.MS5837_30BA")
print(" * pressureSensors.example1")
print(" * pressureSensors.example2")
print(" * pressureSensors.example3")
print("\u001b[0m")
