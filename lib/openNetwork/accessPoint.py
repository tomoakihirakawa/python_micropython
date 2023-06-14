# アクセスポイントを作成します
import network
import esp
import gc  # ガーベッジコレクタ
from time import sleep, sleep_ms
from machine import Pin, PWM

def makeAccessPoint(ssid="my_esp32", password=""):

    esp.osdebug(None)

    gc.collect()

    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ssid)
    ap.active(True)

    while ap.active() == False:
        sleep(.01)
        pass

    print("------ access point: ssid = \033[0;31m%s\033[0m -------" % ssid)
    print(ap.ifconfig())
    print("")

    return ap

def connectEspToRouter(ssid, password):

    esp.osdebug(None)

    gc.collect()

    st = network.WLAN(network.STA_IF)
    st.active(True)
    st.connect(ssid, password)

    while st.isconnected() == False:
        sleep(.01)
        pass

    print("------ access point: ssid = \033[0;31m%s\033[0m -------" % ssid)
    print(st.ifconfig())
    print("")

    return st

def connectToNetwork(**kwargs):
    
    ssid=kwargs.get('ssid', kwargs.get('SSID', None))        
    pwd=kwargs.get('pass', kwargs.get('PASS', kwargs.get('pwd', kwargs.get('password', None))))

    if ssid and pwd:
        esp.osdebug(None)
        gc.collect()
        st = network.WLAN(network.STA_IF)
        # for t in range(20):
        #     if st.isconnected():
        #             print("------ access point: ssid = \033[0;31m%s\033[0m -------" % ssid)
        #             print(st.ifconfig())
        #             print("")
        #             return st
        #     sleep_ms(70)
        #     if t == 10:
        #         st.active(True)
        #         st.connect(ssid, pwd)        
        st.active(True)
        st.connect(ssid, pwd)
        for t in range(20):
            if st.isconnected():
                    print("------ access point: ssid = \033[0;31m%s\033[0m -------" % ssid)
                    print(st.ifconfig())
                    print("")
                    return st
            sleep(.2)
        st.disconnect()
    return None