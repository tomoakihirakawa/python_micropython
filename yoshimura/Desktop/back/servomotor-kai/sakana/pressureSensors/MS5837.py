
try:
    # microptyhonの場合
    from machine import SoftI2C as I2C, Pin
    import utime as time
    from time import sleep, sleep_us
    
    _MicroPython_ = True
except:
    # ラズパイの場合
    try:
        _MicroPython_ = False
        import smbus
        from time import sleep

        def sleep_us(t):
            sleep(t*(10**-6))

    except:
        print("\u001b[35m")
        print('please install smbus')
        print("\u001b[0m")

from libi2c import *

# Models
MODEL_02BA = 0
MODEL_30BA = 1

# Oversampling options
OSR_256 = 0
OSR_512 = 1
OSR_1024 = 2
OSR_2048 = 3
OSR_4096 = 4
OSR_8192 = 5

# kg/m^3 convenience
DENSITY_FRESHWATER = 997
DENSITY_SALTWATER = 1029

# Conversion factors (from native unit, mbar)
UNITS_Pa = 100.0
UNITS_hPa = 1.0
UNITS_kPa = 0.1
UNITS_mbar = 1.0
UNITS_bar = 0.001
UNITS_atm = 0.000986923
UNITS_Torr = 0.750062
UNITS_psi = 0.014503773773022

# Valid units
UNITS_Centigrade = 1
UNITS_Farenheit = 2
UNITS_Kelvin = 3

# -------------------------------------------------------- #

class MS5837:

    # Registers
    _MS5837_ADDR = 0x76
    # 
    _MS5837_RESET = 0x1E
    _MS5837_ADC_READ = 0x00
    _MS5837_PROM_READ = 0xA0
    _MS5837_CONVERT_D1_256 = 0x40
    _MS5837_CONVERT_D2_256 = 0x50

    def __init__(self, model=MODEL_30BA, **kwargs):

        self.bus=kwargs.get('bus', None)        

        self._model = model
        
        if not self.bus:        
            if _MicroPython_:
                self.bus = I2C(scl=Pin(kwargs.get('scl', 22)), sda=Pin(kwargs.get('sda', 21)))
                print('MS5837 for micropython')
                print('self.bus.scan()  ', self.bus.scan() )
            else:
                self.bus = smbus.SMBus(kwargs.get('busnum', 1))


        self._fluidDensity = DENSITY_FRESHWATER
        self._pressure = 0
        self._temperature = 0
        self._D1 = 0
        self._D2 = 0
        
        self.init();

    def bytes2int(self, firstbyte, secondbyte):
        if _MicroPython_:
            # オーバーフローのチェック
            if not firstbyte & 0x80:
                return (firstbyte << 8) + secondbyte
            return - (((firstbyte ^ 255) << 8) + (secondbyte ^ 255) + 1)
        else:
            value = (firstbyte << 8) + secondbyte
            return value

    def init(self):
        if self.bus is None:
            "No bus!"
            return False

        # self.bus.write_byte(self._MS5837_ADDR, self._MS5837_RESET)

        # print(b"{}".format(self._MS5837_RESET))
        # self.bus.writeto(self._MS5837_ADDR, b"{}".format(self._MS5837_RESET))
        write_byte(self.bus,self._MS5837_ADDR, self._MS5837_RESET)
        
        # Wait for reset to complete
        sleep(0.05)

        self._C = []
        # Read calibration values and CRC
        for i in range(7):
            c = read_byte_data(self.bus, self._MS5837_ADDR, self._MS5837_PROM_READ + 2*i, 2)
            value = (c[0] << 8) + c[1]
            self._C.append(value)
        
        print(self._C)
        
        crc = (self._C[0] & 0xF000) >> 12
        if crc != self._crc4(self._C):
            #PROM: Programmable Read-Only Memory
            #CRC: cyclic redundancy check
            print("PROM read error, CRC failed!")
            return False

        return True

    def read(self, oversampling=OSR_4096):
        if self.bus is None:
            print("No bus!")
            return False

        if oversampling < OSR_256 or oversampling > OSR_8192:
            print("Invalid oversampling option!")
            return False

        # Request D1 conversion (pressure)
        # self.bus.write_byte(self._MS5837_ADDR, self._MS5837_CONVERT_D1_256 + 2*oversampling)
        write_byte(self.bus,self._MS5837_ADDR, self._MS5837_CONVERT_D1_256 + 2*oversampling)

        # Maximum conversion time increases linearly with oversampling
        # max time (seconds) ~= 2.2e-6(x) where x = OSR = (2^8, 2^9, ..., 2^13)
        # We use 2.5e-6 for some overhead
        # sleep(2.5e-6 * 2**(8+oversampling))
        sleep_us(round(10**6*(2.5e-6 * 2**(8+oversampling))))

        # d = self.bus.read_i2c_block_data(
        #     self._MS5837_ADDR, self._MS5837_ADC_READ, 3)
        
        d = read_byte_data(self.bus,self._MS5837_ADDR, self._MS5837_ADC_READ, 3)
        
        self._D1 = d[0] << 16 | d[1] << 8 | d[2]

        # Request D2 conversion (temperature)
        # self.bus.write_byte(self._MS5837_ADDR, self._MS5837_CONVERT_D2_256 + 2*oversampling)

        write_byte(self.bus,self._MS5837_ADDR, self._MS5837_CONVERT_D2_256 + 2*oversampling)

        # As above
        # sleep(2.5e-6 * 2**(8+oversampling))
        sleep_us(round(10**6*(2.5e-6 * 2**(8+oversampling))))


        # d = self.bus.read_i2c_block_data(self._MS5837_ADDR, self._MS5837_ADC_READ, 3)
        d = read_byte_data(self.bus,self._MS5837_ADDR, self._MS5837_ADC_READ, 3)
        self._D2 = d[0] << 16 | d[1] << 8 | d[2]

        # Calculate compensated pressure and temperature
        # using raw ADC values and internal calibration
        self._calculate()

        return True

    def setFluidDensity(self, denisty):
        self._fluidDensity = denisty

    # Pressure in requested units
    # mbar * conversion
    def pressure(self, conversion=UNITS_kPa):
        #UNITS_mbar
        return self._pressure * conversion

    # Temperature in requested units
    # default degrees C
    def temperature(self, conversion=UNITS_Centigrade):
        degC = self._temperature / 100.0
        if conversion == UNITS_Farenheit:
            return (9.0/5.0)*degC + 32
        elif conversion == UNITS_Kelvin:
            return degC + 273
        return degC

    # Depth relative to MSL pressure in given fluid density
    def depth(self):
        return (self.pressure(UNITS_Pa)-101300)/(self._fluidDensity*9.80665)

    # Altitude relative to MSL pressure
    def altitude(self):
        return (1-pow((self.pressure()/1013.25), .190284))*145366.45*.3048

    # Cribbed from datasheet
    def _calculate(self):
        OFFi = 0
        SENSi = 0
        Ti = 0

        dT = self._D2-self._C[5]*256
        if self._model == MODEL_02BA:
            SENS = self._C[1]*65536+(self._C[3]*dT)/128
            OFF = self._C[2]*131072+(self._C[4]*dT)/64
            self._pressure = (self._D1*SENS/(2097152)-OFF)/(32768)
        else:
            SENS = self._C[1]*32768+(self._C[3]*dT)/256
            OFF = self._C[2]*65536+(self._C[4]*dT)/128
            self._pressure = (self._D1*SENS/(2097152)-OFF)/(8192)

        # 以前のもの
        self._temperature = 2000+dT*self._C[6]/8388608
        
        # beta = 0.9
        # tmp = (2000+dT*self._C[6]/8388608)
        # self._temperature = self._temperature*0.5 + tmp*0.5

        # Second order compensation
        if self._model == MODEL_02BA:
            if (self._temperature/100) < 20:  # Low temp
                Ti = (11*dT*dT)/(34359738368)
                OFFi = (31*(self._temperature-2000)*(self._temperature-2000))/8
                SENSi = (63*(self._temperature-2000)
                         * (self._temperature-2000))/32

        else:
            if (self._temperature/100) < 20:  # Low temp
                Ti = (3*dT*dT)/(8589934592)
                OFFi = (3*(self._temperature-2000)*(self._temperature-2000))/2
                SENSi = (5*(self._temperature-2000)*(self._temperature-2000))/8
                if (self._temperature/100) < -15:  # Very low temp
                    OFFi = OFFi+7*(self._temperature+1500) * \
                        (self._temperature+1500)
                    SENSi = SENSi+4*(self._temperature+1500) * \
                        (self._temperature+1500)
            elif (self._temperature/100) >= 20:  # High temp
                Ti = 2*(dT*dT)/(137438953472)
                OFFi = (1*(self._temperature-2000)*(self._temperature-2000))/16
                SENSi = 0

        OFF2 = OFF-OFFi
        SENS2 = SENS-SENSi

        if self._model == MODEL_02BA:
            self._temperature = (self._temperature-Ti)
            self._pressure = (((self._D1*SENS2)/2097152-OFF2)/32768)/100.0
        else:
            self._temperature = (self._temperature-Ti)
            self._pressure = (((self._D1*SENS2)/2097152-OFF2)/8192)/10.0

    # Cribbed from datasheet
    def _crc4(self, n_prom):
        n_rem = 0
        n_prom[0] = ((n_prom[0]) & 0x0FFF)
        n_prom.append(0)

        for i in range(16):
            if i % 2 == 1:
                n_rem ^= ((n_prom[i >> 1]) & 0x00FF)
            else:
                n_rem ^= (n_prom[i >> 1] >> 8)

            for n_bit in range(8, 0, -1):
                if n_rem & 0x8000:
                    n_rem = (n_rem << 1) ^ 0x3000
                else:
                    n_rem = (n_rem << 1)

        n_rem = ((n_rem >> 12) & 0x000F)

        self.n_prom = n_prom
        self.n_rem = n_rem

        return n_rem ^ 0x00


if _MicroPython_:
    class MS5837_30BA(MS5837):
        def __init__(self,**kwargs):
            MS5837.__init__(self, MODEL_30BA, **kwargs)

    class MS5837_02BA(MS5837):
        def __init__(self,**kwargs):
            MS5837.__init__(self, MODEL_02BA,**kwargs)   
           
else:
    class MS5837_30BA(MS5837):
        def __init__(self, **kwargs):
            MS5837.__init__(self, MODEL_30BA, **kwargs)


    class MS5837_02BA(MS5837):
        def __init__(self, **kwargs):
            MS5837.__init__(self, MODEL_02BA, **kwargs)



def example():
    s = MS5837_30BA()
    for t in range(1000):
        # sleep(.01)
        if s.read():
            print("P: %0.4f kPa\tT: %0.2f" % (s.pressure(), s.temperature()))
        else:
            print("Sensor read failed!")
            exit(1)


def example2():
    s = MS5837_30BA()
    s.read()
    p = s.depth()    
    beta = 0.8
    for t in range(10000):
        sleep(.01)
        if s.read():            
            p = p*beta + s.depth()*(1-beta)
            print("P: %0.4f m\tT: %0.2f" % (p, s.temperature()))
        else:
            print("Sensor read failed!")
            exit(1)

def example3():
    s = MS5837_30BA()
    s.read()
    p = s.depth()    
    beta = 0.7
    ar =["*"]
    for t in range(10000):
        sleep(.05)
        if s.read():            
            p = p*beta + s.depth()*(1-beta)
            print(("\u001b[3"+str(int(100*p))+"m"+"P:%0.5f, %s m\u001b[0m,  T: %0.5f") % (p,' '.join(int(p*1000)*ar).replace(" ",""), s.temperature()))
        else:
            print("Sensor read failed!")
            exit(1)

if __name__ == '__main__':
    example3()