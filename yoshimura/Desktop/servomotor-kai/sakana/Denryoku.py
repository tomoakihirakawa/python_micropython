
import smbus
from time import sleep
import ctypes

from INA226 import ina226, demo

i2c = smbus.SMBus(1)



INA226_ADDRESS = 0x41


try:
    print("Configuring INA226..")
    iSensor = ina226(INA226_ADDRESS,1)
    iSensor.configure()
    iSensor.calibrate(rShuntValue = 0.002, iMaxExcepted = 10)
    
    sleep(1)
    
    # print "Configuration Done"
    
    current = iSensor.readShuntCurrent()
    
    print("Current Value is ",str(current),"A")
    
    # print "Mode is "+str(hex(iSensor.getMode()))

    A = 0
    P = 0
    V = 0
    a = 0.7
    for i in range(1000):
        sleep(0.1)    
        V = V*(1-a) + iSensor.readBusVoltage() *a
        P = P*(1-a) + iSensor.readBusPower() *a
        A = A*(1-a) +  iSensor.readShuntCurrent()*a
        print("V = ", V, ", A = ",A, ", P = ", P)

    while True:
        # print "Current: "+str(round(iSensor.readShuntCurrent(),3))+"A"+", Voltage: "+str(round(iSensor.readBusVoltage(),3))+"V"+", Power:"+str(round(iSensor.readBusPower(),3))+"W"
        #print "ShuntBus_Voltage: "+str(iSensor.readShuntVoltage())
        sleep(0.2)

except KeyboardInterrupt as e:
    # print '\nCTRL^C received, Terminating..'        
    iSensor.close()

except Exception as e:
    # print "There has been an exception, Find detais below:"
    # print str(e)
    iSensor.close()

