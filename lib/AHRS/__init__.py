from .MPU6050 import MPU6050
from .AK8963 import AK8963
from .MPU9250 import MPU9250
# from AHRS.fusion import fusion

# これによってAHRS.MPU6050としてMPU6050.MPU6050がつかえるようになる
print("\u001b[35m")
print("AHRS is imported")
print("You can use:")
print(" * AHRS.MPU6050")
print(" * AHRS.AK8963")
print(" * AHRS.MPU9250")
print(" * AHRS.fusion")
print("\u001b[0m")
