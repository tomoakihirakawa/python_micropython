
try:
    import machine
    machine.freq(240000000)
    from python_shared_lib.openNetwork import *
    try:
        from machine import Pin
        led = Pin(19, Pin.OUT)
        led.off()
    except:
        pass
    # DummySensorServer()
    DummyMPUServer(monitor_size=(128, 64))

    # DummyMPUServer(monitor_size=(64, 32))
    # DummyPressureSensorServer(monitor_size=(128, 64))
    # DummyAccelStepperMotorServer(monitor_size=(128, 64))
    # DummyStepperMotorServer(monitor_size=(128, 64))
    # DummyFactoryServer(port=40000)
    # DummyServoMotorServer(monitor_size=(128, 64), ch=[0])
except:
    pass
