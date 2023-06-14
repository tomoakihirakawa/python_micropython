_black_ = "\u001b[30m"
_red_ = "\u001b[31m"
_green_ = "\u001b[32m"
_yellow_ = "\u001b[33m"
_blue_ = "\u001b[34m"
_magenta_ = "\u001b[35m"
_cyan_ = "\u001b[36m"
_white_ = "\u001b[37m"
_default_color_ = "\u001b[0m"

# -------------------------------------------------------- #

"""
from openNetwork import *
とすれば，パッケージ名なしで，関数を呼び出せる
"""
try:
    from .accessPoint import makeAccessPoint
    from .accessPoint import connectEspToRouter

    print(_green_+"accessPoint is imported"+_default_color_)
    print(_green_+"You can use:"+_default_color_)
    print(_green_+" * openNetwork.makeAccessPoint"+_default_color_)
    print(_green_+" * openNetwork.connectEspToRouter"+_default_color_)
except:
    print(_red_+"accessPoint is not imported"+_default_color_)
    print(_red_+"You can use:"+_default_color_)
    print(_red_+" x openNetwork.makeAccessPoint"+_default_color_)
    print(_red_+" x openNetwork.connectEspToRouter"+_default_color_)

# -------------------------------------------------------- #
print(_green_+"openNetwork is imported"+_default_color_)

try:
    from .ServerUDP import ServerUDP
    print(_green_+" * openNetwork.ServerUDP"+_default_color_)
except:
    print(_red_+" x openNetwork.ServerUDP"+_default_color_)

try:
    from .ServerUDP import MediatorUDP
    print(_green_+" * openNetwork.MediatorUDP"+_default_color_)
except:
    print(_red_+" x openNetwork.MediatorUDP"+_default_color_)

try:
    from .ServerUDP import RecieverUDP
    print(_green_+" * openNetwork.RecieverUDP"+_default_color_)
except:
    print(_red_+" x openNetwork.RecieverUDP"+_default_color_)

try:
    from .ServerUDP import DummySensorServer
    print(_green_+" * openNetwork.DummySensorServer"+_default_color_)
except:
    print(_red_+" x openNetwork.DummySensorServer"+_default_color_)

try:
    from .ServerUDP import DummyServoMotorServer
    print(_green_+" * openNetwork.DummyServoMotorServer"+_default_color_)
except:
    print(_red_+" x openNetwork.DummyServoMotorServer"+_default_color_)

try:
    from .ServerUDP import DummyStepperMotorServer
    print(_green_+" * openNetwork.DummyStepperMotorServer"+_default_color_)
except:
    print(_red_+" x openNetwork.DummyStepperMotorServer"+_default_color_)

try:
    from .ServerUDP import DummyAccelStepperMotorServer
    print(_green_+" * openNetwork.DummyAccelStepperMotorServer"+_default_color_)
except:
    print(_red_+" x openNetwork.DummyAccelStepperMotorServer"+_default_color_)


try:
    from .ServerUDP import DummyPressureSensorServer
    print(_green_+" * openNetwork.DummyPressureSensorServer"+_default_color_)
except:
    print(_red_+" x openNetwork.DummyPressureSensorServer"+_default_color_)


try:
    from .ServerUDP import DummyMPUServer
    print(_green_+" * openNetwork.DummyMPUServer"+_default_color_)
except:
    print(_red_+" x openNetwork.DummyMPUServer"+_default_color_)

try:
    from .ServerUDP import DummyFactoryServer
    print(_green_+" * openNetwork.DummyFactoryServer"+_default_color_)
except:
    print(_red_+" x openNetwork.DummyFactoryServer"+_default_color_)
