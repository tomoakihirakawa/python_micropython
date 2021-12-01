
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
    # DummyPressureSensorServer()
    # DummyStepperMotorServer()
    # DummyFactoryServer(port=40000)
    # DummyServoMotorServer(ch=[0,1,2,3])
except:
    pass
