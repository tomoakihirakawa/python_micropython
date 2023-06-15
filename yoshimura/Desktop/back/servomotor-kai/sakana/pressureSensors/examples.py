

from time import sleep 
from pressureSensors import MS5837_30BA
def example1():
    #圧力をターミナル上に表示する例
    # from pressureSensors import MS5837_02BA
    #センサークラスを生成
    sensor = MS5837_30BA()

    for t in range(1000):
        sleep(.1)
        if sensor.read():
            print("P: %0.1f kPa\tT: %0.2f" % (sensor.pressure(), sensor.temperature()))
        else:
            print("Sensor read failed!")
            exit(1)
            

def example2():
    #matplotlibを使って圧力の変化を表示する例
    # from pressureSensors import MS5837_02BA

    #センサークラスを生成
    sensor = MS5837_30BA()

    count = 0

    import matplotlib.pyplot as plt
    # import numpy as np
    fig = plt.figure()#図を生成
    plt.grid()
    ax = fig.add_subplot(111)  # fig内部に軸を生成
    minmax = [1000,3000]
    ax.set_xlim(minmax)
    ax.set_ylim(minmax)
    ax.set_xlabel('sec')
    ax.set_ylabel('kPa')
    ax_, = ax.plot([],[])

    T=[]
    P=[]
    Tstart = time()
    for t in range(1000):
        if sensor.read():
            # --------- 計測結果 ------ #
            T.append(time()-Tstart) 
            P.append(sensor.pressure())
            ax_.set_xdata(T)
            ax_.set_ydata(P)
            if t > 1:
                ax.set_xlim(T[0], T[-1])
            plt.pause(0.05)
            
            
def example3():
    s = MS5837_30BA()
    sleep(.01)
    s.read()
    sleep(.01)
    p = s.depth()
    sleep(.01)
    offset = p
    beta = 0.8
    ar =["*"]
    
    for t in range(10000):
        sleep(.01)
        if s.read():            
            p = p*beta + s.depth()*(1-beta) - offset
            color = "\u001b[3"+str(int(100*p))+"m"
            print((color+" depth:%0.5f,%s m\u001b[0m,  T: %0.5f") % (p,' '.join(int(p*1000)*ar).replace(" ",""), s.temperature()))
        else:
            print("Sensor read failed!")
            exit(1)
