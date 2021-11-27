
"""
keep_updateをスレッドで実行し，グローバル変数tを変更し続ける．
同時に，whileループで内部でソケットを使ってメッセージを受け取り続ける．
クライアントからのメッセージはJSON形式でキーに応じて実行する関数を決める．
"""

try:
    from machine import Pin, SoftI2C
    import math
    import usocket as socket
    from utime import sleep, time, time_ns, sleep_ms, sleep_us
    import ujson as json
    import _thread
    import sys
    # @ 独自のネットワーク接続用ライブラリ
    from .accessPoint import *
    try:
        from display import *
    except:
        pass
    _MicroPython_ = True
except:
    import socket
    from time import sleep, time, time_ns
    import json
    import threading

    def sleep_ms(t):
        sleep(t*(10**-3))

    def sleep_us(t):
        sleep(t*(10**-6))

    def get_ip_address():
        try:
            ip_address = ''
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
            s.close()
            return ip_address
        except:
            print('ネットワークに繋がっていないのでは？')

    _MicroPython_ = False


def sleep_ns(t):
    sleep_us(round(t*(10**-3)))

#@ -------------------------------------------------------- #
#@                エンコードとデコードの関数                    #
#@ -------------------------------------------------------- #


def decode_bytes(j):
    ret = j.decode("utf-8").replace("'", '"')
    try:
        return json.loads(ret)
    except:
        return ret


if _MicroPython_:
    def jsonToBytes(j):
        return b"{}".format(json.dumps(j))
else:
    def jsonToBytes(j):
        return bytes(json.dumps(j), encoding='utf-8')

"""
p:クライアントが'change'というキーをもつJSONを送ってきたら変更される
a,w,dt:サーバーのkeep_update関数で変更され続ける
"""


class pacer():

    def __init__(self):
        self.wakeupAt = time_ns()
        self.total_time = 0
        self.min_time = 0
        self.sleep_time = 0

    def pace(self, period_in_sec):
        # ------------------------- 時間調整 ------------------------- #
        # 眠る時間 = 設定した時間間隔 - (現在 - 以前起きた時刻)
        self.min_time = (time_ns()-self.wakeupAt)
        self.sleep_time = round(period_in_sec*10**9 - self.min_time - 1533000)
        if self.sleep_time > 0:
            sleep_ns(self.sleep_time)
        tmp = time_ns()
        self.total_time = tmp - self.wakeupAt
        self.wakeupAt = tmp
        sleep(period_in_sec*0.1)
        # ----------------------------------------------------------- #

#% -------------------------------------------------------- #
#%           User Datagram Protocol (UDP) sockets           #
#% -------------------------------------------------------- #

# UDPは信頼できる通信方法ではない．データの順番が不明
# https://realpython.com/python-sockets/


class ServerUDP():

    def __del__(self):
        try:
            self.process_server.close()
            self.sender_server.close()
            print('process serverをclose')
            print('sender serverをclose')
        except:
            pass

    def __init__(self, **kwargs):
        """
        server    port                  Mediator  port
        # --------------------------------------------- #
        process   50000  <------------  process   50000
        sender    50001  -- _STATE -->  receiver  50001
        """
        self.ssid = kwargs.get('ssid', kwargs.get('SSID', "RaspberryPi"))
        self.password = kwargs.get('password', kwargs.get(
            'PASS', kwargs.get('pwd', kwargs.get('pass', "RaspberryPi"))))
        self.PORT = kwargs.get('port', kwargs.get('PORT', 50000))
        self.BUFFSIZE = kwargs.get(
            'buff', kwargs.get('BUFF', kwargs.get('size', 256)))
        self.display = kwargs.get('display', None)
        self.text_to_display = ["", "", "", "", "", ""]
        #
        self.monitor_width, self.monitor_height = kwargs.get(
            'monitor_size', (64, 32))
        self.activate_process_loop = kwargs.get(
            'activate_process_loop', True)

        # -------------------------------------------------------- #
        # self.clients_list = []
        self.client = None
        self._STATE = {"period": 5.0}
        # -------------------------------------------------------- #
        #         MicroPythonの場合 ネットワークへの接続               #
        print("MicroPythonの場合 ネットワークへの接続")
        # -------------------------------------------------------- #
        if _MicroPython_ and self.ssid:
            # esp32の場合は，まずネットワークに接続する．
            # ap = connectEspToRouter(self.ssid, self.password)
            self.display_text(str(self.ssid), 0)
            ap = connectToNetwork(ssid=self.ssid, pwd=self.password)
            if not ap:
                try:
                    inputfile = open('ssid_pwd.json', encoding='utf-8')
                    print("ssid_pwd.json has opened")
                    ssid_pwd = json.load(inputfile)
                    inputfile.close()
                    for i in range(10):
                        for ssid, pwd in ssid_pwd.items():
                            if not ap:
                                self.ssid = ssid
                                self.password = pwd
                                self.display_text(str(self.ssid), 0)
                                ap = connectToNetwork(
                                    ssid=self.ssid, pwd=self.password)
                            else:
                                break
                except IOError:
                    print("ssid_pwd.json can not be opened")

            self.HOST = ap.ifconfig()[0]
        else:
            # ラズパイの場合は，ネットワークに接続済みだろうから，接続しているipアドレスを取得する
            self.HOST = get_ip_address()

        print("# -------------------------------------------------------- #")
        print('ホストアドレスは', self.HOST)
        print('送信周期，periodは', self._STATE['period'], '秒です')
        print("# -------------------------------------------------------- #")

        # -------------------------------------------------------- #
        #                           モニター                         #
        # -------------------------------------------------------- #
        print("モニター")
        # self.display_text('id:' + str(self.ssid), 0, 0, 1)
        # self.display_text('h:' + str(self.HOST), 0, 17, 2)
        # self.display_text('p:' + str(self.PORT), 0, 17+10, 2)
        self.text_to_display = [str(self.ssid),
                                str(self.HOST),
                                str(self.PORT), "", "", ""]
        self.show()  # first row
        # -------------------------------------------------------- #
        #                           ソケット                        #
        # -------------------------------------------------------- #
        print("ソケット")
        #! ----------------------- processソケット ---------------------- #
        self.process_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        processHP = (self.HOST, self.PORT)
        self.process_server.bind(processHP)
        self.process_server.setblocking(False)
        print('process serverを', processHP, 'にバインド')
        #! ------------------- senderソケット ------------------- #
        self.sender_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        senderHP = (self.HOST, self.PORT+1)
        self.sender_server.bind(senderHP)
        self.sender_server.setblocking(False)
        # print('sender serverを', senderHP, 'にバインド')
        # """
        # senderループは頻繁に実行する同期的プロセスなので，スレッドの実行は派生クラスに委ねる
        # """
        sleep(0.1)
        # -------------------------------------------------------- #
        #                  プロセスのリスナーループ                    #
        # -------------------------------------------------------- #
        if self.activate_process_loop:
            print("リスナーループを開始")
            try:
                self.thread_process_loop = _thread.start_new_thread(
                    self.process_loop, ())
                print("process_loopを開始（Micropython）")
            except:
                self.thread_process_loop = threading.Thread(
                    target=self.process_loop, args=())
                self.thread_process_loop.setDaemon(True)
                self.thread_process_loop.start()
                print("process_loopを開始")
        # -------------------------------------------------------- #
        sleep(0.1)
        # 点滅
        self.led = None
        try:
            self.led = Pin(19, Pin.OUT)
        except:
            pass

        self._FUNCTIONS = {"set": self.setState}
    # -------------------------------------------------------- #

    def display_scroll(self, i):
        self.show(i)

    def display_text(self, text, line):
        self.text_to_display[line] = text
        self.show()

    def show(self, scroll=0):
        color = 1
        width = self.monitor_width
        height = self.monitor_height
        try:
            self.display = self.display if self.display else SSD1306_I2C(
                width, height, SoftI2C(scl=Pin(22), sda=Pin(21)))
            self.display.fill_rect(
                0, 0, self.display.width, self.display.height, 0)

            for i in range(len(self.text_to_display)):
                self.display.text(self.text_to_display[i], scroll, 10*i, color)
            self.display.show()
        except:
            print(self.text_to_display)
            print("エラー")
            pass

        # self.display = self.display if self.display else SSD1306_I2C(
        #     128, 64, SoftI2C(scl=Pin(22), sda=Pin(21)))
        # self.display.fill_rect(x, y, self.display.width,
        #                        self.display.height, 0)
        # self.display.text(text, x, y, color)
        # self.display.show()
    # -------------------------------------------------------- #
    #                          process                          #
    # -------------------------------------------------------- #

    def setState(self, jsn):
        try:
            self._STATE.update((k, jsn[k]) for k in set(
                self._STATE.keys()).intersection(set(jsn.keys())))
            print(self._STATE)
        except:
            print('invalid json ', jsn, '\n cannot be set')

    def process_loop(self, timeout=0):
        """
        基本はポート50001
        """
        jsn = ''
        r_msg = None
        client = None
        while True:
            try:
                if self.monitor_width < 64:
                    self.display_scroll(round(-a+a*math.cos(2.*math.pi*i/1.5)))
                # ---------------------------------- #
                r_msg, client = self.process_server.recvfrom(128)
                jsn = decode_bytes(r_msg)
                print("\u001b[35maccessed from ",
                      client, " : ", jsn, "\u001b[0m")
                self.add_remove_client(client)
                try:
                    for key, value in jsn.items():
                        fun = self._FUNCTIONS.get(key)
                        if fun is not None:
                            print("\u001b[35mThe function is found\u001b[0m")
                            try:
                                fun(value)
                            except:
                                try:
                                    fun()
                                except:
                                    print('\u001b[35mThe function is found but argument is not valid',
                                          key, value, "\u001b[0m")
                        else:
                            print('\u001b[35mcannot find function ',
                                  self._FUNCTIONS.items(), "\u001b[0m")
                            pass
                except:
                    print('\u001b[35minvalid type of message',
                          jsn, "\u001b[0m")
                    pass
            except:
                pass

    # -------------------------------------------------------- #
    #                          sender                          #
    # -------------------------------------------------------- #

    def start_sender(self):

        if _MicroPython_:
            self.thread_sender_loop = _thread.start_new_thread(
                self.sender_loop, ())
        else:
            self.thread_sender_loop = threading.Thread(
                target=self.sender_loop, args=())
            self.thread_sender_loop.setDaemon(True)
            self.thread_sender_loop.start()
        print("sender_loopをスレッドを使って開始")

    def sender_loop(self):
        """
        クライアントが登録されていれば，周期的に送信する
        sleep時間を変化させ出来るだけ一定周期にしている
        """
        P = pacer()
        while True:
            # self.led.on()
            # メモ：
            # クライアント側でつながっているポートは，クライアントからのメッセージが送られてきた際に得ることができる．
            # cは，(ip address, port)のタプル型．
            # ここのポートは，このサーバーにおけるポートではなく，クライアント自身のポート
            # -------------------------------------------------------- #
            P.pace(self._STATE["period"])
            # 送信にかかる実際の時間
            print(self._STATE)
            self.send()
            # 点滅
            # -------------------------------------------------------- #
            # 前回の送信単体でかかってしまった時間．短縮できないもの（0.01?）
            self._STATE.update({"t_work": P.min_time*10**-9,
                                "t_tot": P.total_time*10**-9})

    def send(self):
        if self.led:
            self.led.on()
            self.sender_server.send(jsonToBytes(self._STATE))
            self.led.off()
        else:
            self.sender_server.send(jsonToBytes(self._STATE))

    # -------------------------------------------------------- #

    def add_remove_client(self, client):
        """
        この関数でクライエントを追加するか，リストから削除するかなどを決める．
        """
        # if not (client in self.clients_list):
        #     for c in list(filter(lambda c: c[0] == client[0], self.clients_list)):
        #         self.clients_list.remove(c)
        #     self.clients_list.append(client)
        if not client == self.client:
            print("\u001b[35m")
            try:
                print("new client ", self.client)
                self.sender_server.connect((client[0], client[1]+1))
                self.client = client
                print("コネクト成功")
                # y = 17+10+10+5
                y = 10+10+10+5
                h = 10
                # self.display_text('c:' + str(client[0]), 0, y, 1)
                # y = y + h
                # self.display_text('p:' + str(client[1]), 0, y, 1)
                self.display_text(str(client[0]), 2)
                y = y + h
                self.display_text(str(client[1]), 3)

            except:
                print("コネクト失敗")
                pass

            print("\u001b[0m")


#@ -------------------------------------------------------- #
#@        サーバーからデータを取得することを仲介してくれる          #
#@ -------------------------------------------------------- #

class MediatorUDP():

    def __del__(self):
        try:
            self.process_server.close()
            self.receiver_server.close()
            print('process serverをclose')
            print('receiver serverをclose')
        except:
            pass

    def __init__(self, **kwargs):
        # 小文字
        self.REMOTE = kwargs.get('remote', kwargs.get('REMOTE', None))
        if not self.REMOTE:
            raise Exception(
                "\u001b[31mplease enter a valid remote address\u001b[0m")
        self.HOST = kwargs.get('host', kwargs.get('HOST', get_ip_address()))
        self.REMOTE_PORT = kwargs.get('remote_port', 50000)
        self.HOST_PORT = kwargs.get('host_port', kwargs.get('port', 50000))
        self.BUFFSIZE = kwargs.get('buff', kwargs.get('BUFF', 256))
        # 大文字
        self._STATE = {'period': 5.0}
        # -------------------------------------------------------- #
        """
        server    port                  Mediator  port
        # --------------------------------------------- #
        process   50000  <------------  process   50000
        sender    50001  -- _STATE -->  receiver  50001
        """

        self.process_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.processHP = (self.HOST, self.HOST_PORT)
        self.process_server.bind(self.processHP)
        self.processRP = (self.REMOTE, self.REMOTE_PORT)

        # レシーバーだけがメッセージを受け取る
        self.receiverHP = (self.HOST, self.HOST_PORT+1)
        self.receiver_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receiver_server.bind(self.receiverHP)
        # self.receiver_server.settimeout(0.)と同じ
        # self.receiver_server.setblocking(True)

        # -------------------------------------------------------- #

        print('リモートアドレスは', self.REMOTE)
        print('ホストアドレスは', self.HOST)
        print('process serverを', self.processHP, 'にバインド')
        print('receiver serverを', self.receiverHP, 'にバインド')

        print("receiver_loopをスレッドを使って開始")
        if _MicroPython_:
            self.thread_receiver_loop = _thread.start_new_thread(
                self.receiver_loop, ())
        else:
            self.thread_receiver_loop = threading.Thread(
                target=self.receiver_loop, args=())
            self.thread_receiver_loop.setDaemon(True)
            self.thread_receiver_loop.start()

    def receiver_loop(self):
        """
        レシーバーは，_STATEの情報を受け取り，それを自身の_STATEにコピーする
        """
        while True:
            try:
                self._STATE.update(decode_bytes(
                    self.receiver_server.recv(self.BUFFSIZE)))
            except:
                sleep(0.001)
                pass

    def __call__(self, key=None):
        if key:
            self.process_server.sendto(jsonToBytes(key), self.processRP)
        return self._STATE

    def get(self, key=None):
        return self._STATE.get(key)

    def monitor(self, t=0.1):
        for i in range(10000):
            sleep(t)
            print(self._STATE)


#@ -------------------------------------------------------- #
#@                     RecieverUDP                          #
#@ -------------------------------------------------------- #

try:
    with open("./setting.json", 'r') as json_file:
        data = json.load(json_file)
        print(data)
except:
    print('setting.json is not found')
    pass


class RecieverUDP():

    def __del__(self):
        try:
            self.receiver_server.close()
            print('process serverをclose')
            print('receiver serverをclose')
        except:
            pass

    def __init__(self, **kwargs):
        # 小文字
        self.HOST = kwargs.get('host', kwargs.get('HOST', get_ip_address()))
        self.REMOTE_PORT = kwargs.get('remote_port', 50000)
        self.HOST_PORT = kwargs.get('host_port', kwargs.get('port', 50000))
        self.BUFFSIZE = kwargs.get('buff', kwargs.get('BUFF', 256))
        # 大文字
        self._STATE = {}
        # -------------------------------------------------------- #
        """
        server    port                  Mediator  port
        # --------------------------------------------- #
        process   50000  <------------  process   50000
        sender    50001  -- _STATE -->  receiver  50001
        """

        # レシーバーだけがメッセージを受け取る
        self.receiverHP = (self.HOST, self.HOST_PORT+1)
        self.receiver_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receiver_server.bind(self.receiverHP)
        # self.receiver_server.settimeout(0.)と同じ
        self.receiver_server.setblocking(False)

        # -------------------------------------------------------- #

        print('ホストアドレスは', self.HOST)
        print('receiver serverを', self.receiverHP, 'にバインド')

        print("receiver_loopをスレッドを使って開始")
        if _MicroPython_:
            self.thread_receiver_loop = _thread.start_new_thread(
                self.receiver_loop, ())
        else:
            self.thread_receiver_loop = threading.Thread(
                target=self.receiver_loop, args=())
            self.thread_receiver_loop.setDaemon(True)
            self.thread_receiver_loop.start()

    def receiver_loop(self):
        """
        レシーバーは，_STATEの情報を受け取り，それを自身の_STATEにコピーする
        """
        while True:
            try:
                self._STATE.update(decode_bytes(
                    self.receiver_server.recv(self.BUFFSIZE)))
                sleep(3)
            except:
                pass

    def __call__(self, key=None):
        return self._STATE

    def monitor(self, t=0.1):
        for i in range(10000):
            sleep(t)
            print(self._STATE)

# ----------------------------------------------------------------------------------------- #

# 例
# >> from openNetwork import *
# >> m=MediatorUDP(remote="10.0.1.8",port=5000)
## -------------------------------------------------------- #
##                   通信確認用サーバークラス   　　　　         #
## -------------------------------------------------------- #


class DummySensor():
    def __init__(self):
        print('DummySensor is initialized')
        self.init_time = time_ns()


class DummySensorServer(DummySensor, ServerUDP):

    def __init__(self, **kwargs):
        ServerUDP.__init__(self, **kwargs)
        DummySensor.__init__(self)

        # 自動接続先を設定しておく．
        # try:
        #     # with open("./setting.json", 'r') as json_file:
        #     #     data = json.load(json_file)
        #         # print(data)
        #         # print(data['sending_to'])
        #         # client = (data['sending_to'], 50000)
        #         # self.add_remove_client(client)
        #     self._STATE.update({self.HOST: {"ssid": self.ssid,
        #                                     "port": self.PORT,
        #                                     "buffsize": self.BUFFSIZE,
        #                                     "id": data['id']}})

        # except:
        #     # client = ("10.0.1.3", 50000)
        #     self.add_remove_client(client)
        #     self._STATE.update({self.HOST: {"ssid": self.ssid,
        #                                     "port": self.PORT,
        #                                     "buffsize": self.BUFFSIZE,
        #                                     "id": 999}})

        self._STATE.update({self.HOST: {"ssid": self.ssid,
                                        "port": self.PORT,
                                        "buffsize": self.BUFFSIZE}})

        # while True:
        #     print(self._STATE)
        #     sleep(1)
        #     # self._STATE.update({"実際の周期": 1., "必要時間": 1.})
        #     self.send()

        # -------------------------------------------------------- #
        while True:
            print(self._STATE)
            sleep(self._STATE["period"])
            self.send()
        # -------------------------------------------------------- #


## -------------------------------------------------------- #
##             ステッパーモーターサーバークラス 　　              #
## -------------------------------------------------------- #
try:
    """
    ステッパーモーターを使った例
    """
    from steppermotor import *

    class DummyStepperMotorServer(steppermotor, ServerUDP):
        def __init__(self, **kwargs):
            ServerUDP.__init__(self, **kwargs)
            steppermotor.__init__(self, **kwargs)
            self._FUNCTIONS.update({"freq": self.freq})
            self._FUNCTIONS.update({"accel": self.accel})
            self._FUNCTIONS.update({"start_asymptotic": self.start_asymptotic})
            self._FUNCTIONS.update({"exit_asymptotic": self.exit_asymptotic})
            self._FUNCTIONS.update({"start_sin_wave": self.start_sin_wave})
            self._FUNCTIONS.update({"start_cos_wave": self.start_cos_wave})
            self._FUNCTIONS.update({"exit_wave": self.exit_wave})
except:
    pass

## -------------------------------------------------------- #
##             サーボモーターサーバークラス 　　                 #
## -------------------------------------------------------- #
try:
    """
      +-==-+
    +-+----+-----+
    |            |
    |    MOTOR   |
    |            |
    +------------+
    サーボモーターを使った例
    このパッケージを読み込むディレクトリにservomotorがある必要がある場合読み込まれる
    """
    from servomotor import *

    class DummyServoMotorServer(ServerUDP):
        def repeateMoveAll(self, tup):
            [max, min, num, slp_time] = tup
            for _ in range(num):
                sleep_ms(slp_time)
                for s in self.servomotors.values():
                    s.setDegree(min)
                sleep_ms(slp_time)
                for s in self.servomotors.values():
                    s.setDegree(max)

        def moveDegreeAll(self, tup):
            [max, min, num, slp_time] = tup
            for deg in [min+i*(max-min)/(num-1) for i in range(num)]:
                sleep_ms(slp_time)
                for s in self.servomotors.values():
                    s.setDegree(deg)

        def setDegreeAll(self, deg):
            for s in self.servomotors.values():
                s.setDegree(deg)

        def makeservo(self, i):
            offset = 0
            self.servomotors[str(i)] = servomotor(i, offset)
            print(self.servomotors)
            print('ServoMotor is initialized, ch = ', i, ', offset = ', offset)
            self._FUNCTIONS.update(
                {"setDegree"+str(i): self.servomotors[str(i)].setDegree})
            self._FUNCTIONS.update(
                {"moveDegree"+str(i): self.servomotors[str(i)].moveDegree})

        def __init__(self, **kwargs):
            ServerUDP.__init__(self, **kwargs)
            self.servomotors = {}
            self._FUNCTIONS.update({"makeservo": self.makeservo})
            self._FUNCTIONS.update({"initservo": self.makeservo})
            self._FUNCTIONS.update({"setservo": self.makeservo})
            self._FUNCTIONS.update({"send": self.send})
            self._FUNCTIONS.update({"setDegreeAll": self.setDegreeAll})
            self._FUNCTIONS.update({"moveDegreeAll": self.moveDegreeAll})
            self._FUNCTIONS.update({"repeateMoveAll": self.repeateMoveAll})

except:
    pass
## -------------------------------------------------------- #
##                圧力センサーサーバークラス                    #
## -------------------------------------------------------- #

try:
    """
           +=+--+
    -|-|-|-|=|  |
     | | | |=|  | <=== P
    -|-|-|-|=|  |
           +=+--+

    圧力センサーを使った例
    このパッケージを読み込むディレクトリにservomotorがある必要がある場合読み込まれる
    """
    from pressureSensors import MS5837_30BA

    class PressureSensor(MS5837_30BA):
        def __init__(self, **kwargs):
            MS5837_30BA.__init__(self)

    class DummyPressureSensorServer(PressureSensor, ServerUDP):

        def __init__(self, **kwargs):
            ServerUDP.__init__(self, **kwargs)
            PressureSensor.__init__(self, **kwargs)

            if _MicroPython_:
                self.thread_process_loop = _thread.start_new_thread(
                    self.updater_loop, ())
            else:
                self.thread_process_loop = threading.Thread(
                    target=self.updater_loop, args=())
                self.thread_process_loop.setDaemon(True)
                self.thread_process_loop.start()

            self._STATE.update({self.HOST: {"ssid": self.ssid,
                                            "port": self.PORT,
                                            "buffsize": self.BUFFSIZE}})

        def updater_loop(self):
            P = pacer()
            while True:
                print(self._STATE)
                P.pace(self._STATE["period"])
                if self.read():
                    self._STATE.update({"p": self.pressure(),
                                        "depth": self.depth(),
                                        "temp": self.temperature(),
                                        "t_tot": P.total_time*10**-9,
                                        "t_min": P.min_time*10**-9})
                    self.send()
                else:
                    print("Sensor read failed!")
                    exit(1)

except:
    pass

## -------------------------------------------------------- #
## Attitude and heading reference system (AHRS)サーバークラス #
## -------------------------------------------------------- #

try:
    """
    MPU9250
    +------+
    |:    O|
    |:     |
    |:     |
    |:    O|
    +------+
    """

    from AHRS import *

    class DummyMPUServer(MPU9250, ServerUDP):

        def __init__(self, **kwargs):
            ServerUDP.__init__(self, **kwargs)
            """
            注意：self._STATEは，すでに親クラスで定義されて，値が入っているので，上書きせず，追記すること
            """
            MPU9250.__init__(self)
            self._FUNCTIONS.update(
                {"calibrate_mag": self.AK8963.calibrate,
                    "calibrate_gyro": self.MPU6050.calibrate_gyro,
                    "setOffset": self.AK8963.setOffset,
                    "setLowPass": self.setLowPass,
                    "setScale": self.AK8963.setScale})

            self.MAG = (0, 0, 0)
            self.GYRO = (0, 0, 0)
            self.ACCEL = (0, 0, 0)
            self.alpha = 1.

            start = time_ns()

            A, M, G = self.AMG()
            while True:
                # print(self._STATE)
                # P.pace(self._STATE["period"])
                # self.process(self._STATE["period"])
                sleep(self._STATE["period"])
                try:
                    A, M, G = self.AMG()

                    tmp = (1.-self.alpha)
                    self.ACCEL = (tmp*self.ACCEL[0] + self.alpha*A[0],
                                  tmp*self.ACCEL[1] + self.alpha*A[1],
                                  tmp*self.ACCEL[2] + self.alpha*A[2])

                    self.MAG = (tmp*self.MAG[0] + self.alpha*M[0],
                                tmp*self.MAG[1] + self.alpha*M[1],
                                tmp*self.MAG[2] + self.alpha*M[2])

                    self.GYRO = (tmp*self.GYRO[0] + self.alpha*G[0],
                                 tmp*self.GYRO[1] + self.alpha*G[1],
                                 tmp*self.GYRO[2] + self.alpha*G[2])

                    self._STATE.update(
                        {"gyro": self.GYRO, "mag": self.MAG, "accel": self.ACCEL, "time_ns": time_ns()-start})
                    self.sender_server.send(jsonToBytes(self._STATE))
                except:
                    print("Sensor read failed!")
                    print(A, M, G)
                    print(self.ACCEL, self.MAG, self.GYRO)
                    print(self._STATE)
                    sleep(0.2)
                    pass

        def setLowPass(self, a):
            self.alpha = a


except:
    pass

## -------------------------------------------------------- #
##                     サーバー工場クラス   　　　　             #
## -------------------------------------------------------- #

try:
    def initMPU():
        return DummyMPUServer()

    class DummyFactoryServer(ServerUDP):

        def __init__(self, **kwargs):
            ServerUDP.__init__(self, **kwargs)
            self._FUNCTIONS.update({"initMPU": initMPU})

except:
    pass
