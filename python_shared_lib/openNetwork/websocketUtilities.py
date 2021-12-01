
from time import sleep, sleep_ms
import network
try:
    import uos as os
except:
    import os

try:
    import uselect as select
except:
    import select

from uwebsocket import websocket

try:
    import usocket as socket
except:
    import socket

try:
    import usys as sys
except:
    import sys

from my_lib.fundamental import ConsoleOutput
cout = ConsoleOutput()
red = "\033[0;31m"
green = "\033[0;32m"
yellow = "\033[0;33m"
blue = "\033[0;34m"
magenta = "\033[0;35m"
cyan = "\033[0;36m"
endl = "\033[0m\n"

try:
    import ubinascii as binascii
except:
    import binascii
try:
    import uhashlib as hashlib
except:
    import hashlib

DEBUG = 0


# -------------------------------------------------------- #

# Very simplified client handshake, works for MicroPython's
# websocket server implementation, but probably not for other
# servers.

def client_handshake(sock):
    cl = sock.makefile("rwb", 0)
    cl.write(b"""\
    GET / HTTP/1.1\r
    Host: echo.websocket.org\r
    Connection: Upgrade\r
    Upgrade: websocket\r
    Sec-WebSocket-Key: foo\r
    \r
    """)
    l = cl.readline()
    #    print(l)
    while 1:
        l = cl.readline()
        if l == b"\r\n":
            break

#        sys.stdout.write(l)


class ClientClosedError(Exception):
    pass


class WebSocketConnection:
    def __init__(self, remote_addr, socket, close_callback):
        self.client_close = False
        self._need_check = False

        self.address = remote_addr
        self.socket = socket
        self.ws = websocket(socket, True)
        self.poll = select.poll()
        self.close_callback = close_callback

        self.socket.setblocking(False)
        self.poll.register(self.socket, select.POLLIN)
    # -------------------------------------------------------- #

    def read(self):
        poll_events = self.poll.poll(0)

        if not poll_events:
            return

        # Check the flag for connection hung up
        if poll_events[0][1] & select.POLLHUP:
            self.client_close = True

        msg_bytes = None
        try:
            msg_bytes = self.ws.read()
        except OSError:
            self.client_close = True

        # If no bytes => connection closed. See the link below.
        # http://stefan.buettcher.org/cs/conn_closed.html
        if not msg_bytes or self.client_close:
            raise ClientClosedError()

        return msg_bytes
    
    # -------------------------------------------------------- #

    def write(self, msg):
        try:
            self.ws.write(msg)
        except OSError:
            self.client_close = True

    def is_closed(self):
        return self.socket is None

    def close(self):
        print("Closing connection.")
        self.poll.unregister(self.socket)
        self.socket.close()
        self.socket = None
        self.ws = None
        if self.close_callback:
            self.close_callback(self)


###############################################################
###############################################################

#import websocket_helper
#from ws_connection import WebSocketConnection, ClientClosedError


class WebSocketClient:
    def __init__(self, conn):
        self.connection = conn

    def process(self):
        pass


class WebSocketServer:
    # nio is network interface object
    def __init__(self, page, accesspoint, max_connections=1):
        #サーバーのlistening socket
        self._lsock = None
        self._listen_poll = None
        self._clients = []
        self._max_connections = max_connections
        self._page = page
        self._nio = accesspoint
        
    # -------------------------------------------------------- #

    def start(self, port=80):
        if self._lsock:
            self.stop()
        # ソケットの作成から待機
        self._lsock = socket.socket()
        self._lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        addr = socket.getaddrinfo("", port)[0][-1]
        self._lsock.bind(addr)
        self._lsock.listen(1)
        ## micropythonには，高水準のI/O多重化のselectorsがない
        #! micropythonには，低水準のI/O多重化モジュールのselectがある
        self._listen_poll = select.poll()
        #! 監視するsocketオブジェクトを登録．これで読み込み可能かどうか判断できる．
        self._listen_poll.register(self._lsock)  
        print("WebSocket server started")

    # -------------------------------------------------------- #

    def server_handshake(sock):
        '''
        webkeyを読み込んで返す．
        '''
        clr = sock.makefile("rwb", 0)
        l = clr.readline()
        sys.stdout.write(repr(l))

        webkey = None
        while 1:
            l = clr.readline()
            if not l:
                print("EOF in headers")
                break
            if l == b"\r\n":
                break
            sys.stdout.write(l)
            h, v = [x.strip() for x in l.split(b":", 1)]
            if h == b'Sec-WebSocket-Key':
                webkey = v

        if not webkey:
            return webkey
        else:
            respkey = webkey + b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
            respkey = hashlib.sha1(respkey).digest()
            respkey = binascii.b2a_base64(respkey)[:-1]
            return respkey
        
    # -------------------------------------------------------- #

    def _make_client(self, conn):
        return WebSocketClient(conn)

    # -------------------------------------------------------- #

    def stop(self):
        if self._listen_poll:
            self._listen_poll.unregister(self._lsock)
        self._listen_poll = None
        if self._lsock:
            self._lsock.close()
        self._lsock = None

        for client in self._clients:
            client.connection.close()
        print("Stopped WebSocket server.")
        
    # -------------------------------------------------------- #

    def process_all(self):
        poll_events = self._listen_poll.poll(0)
        #! pollは，[(obj0,event0),(obj1,event1),(obj2,event2),....]を返す
        if poll_events:
            if poll_events[0][1] & select.POLLIN:
                #!監視していたソケットself._lsockがPOLLIN：入力待ちである．
                new_socket, remote_addr = self._lsock.accept()

                cout << "Client connection from: host = %s, port = %s" % remote_addr << endl

                if len(self._clients) >= self._max_connections:
                    print(len(self._clients), ", ", self._max_connections)
                    # Maximum connections limit reached
                    new_socket.setblocking(True)
                    new_socket.sendall("HTTP/1.1 503 Too many connections\n\n")
                    new_socket.sendall("\n")
                    # TODO: Make sure the data is sent before closing
                    sleep(0.1)
                    new_socket.close()
                else:
                    # 既存のコネクション配列の中に，同じアドレスがあれば抜き出す．
                    conn = list(
                        filter(lambda c: c.connection.address == remote_addr, self._clients))
                    if len(conn) != 0:
                        cout << blue << conn[0].connection.read() << endl

                    #!監視していたソケットself._lsockがPOLLIN：入力待ちである．．．．ことを思い出す．
                    respkey = self.server_handshake(new_socket)
                    if respkey:
                        # もし，webkeyの解読に成功したら，ハンドシェイクは，成功．upgradeしますと返信する．
                        new_socket.send(b"""\
                        HTTP/1.1 101 Switching Protocols\r
                        Upgrade: websocket\r
                        Connection: Upgrade\r
                        Sec-WebSocket-Accept: %s\r
                        \r
                        """ % respkey)
                        # さらに，websocketのコネクション配列に追加する．
                        # 現段階で，サーバーはただ結果を受信するだけの構造．．．．．
                        # クライエント毎に対応を設定できるようにすべき
                        self._clients.append(self._make_client(WebSocketConnection(
                            remote_addr, new_socket, self.remove_connection)))
                    else:
                        try:
                            #webkeyがない場合，HTTPでテキストを送りますよ，とまず返信する．
                            new_socket.send(b"""\
                            HTTP/1.1 200 OK\n
                            Connection: close\n
                            Server: WebSocket Server\n
                            Content-Type: text/html\n
                            Access-Control-Allow-Origin: *\n
                            """)
                            length = os.stat(self._page)[6]
                            print(os.stat(self._page))
                            new_socket.sendall(
                                'Content-Length: {}\n\n'.format(length))
                            # Process page by lines to avoid large strings
                            with open(self._page, 'r') as f:
                                for line in f:
                                    if line.find("%s") != -1:
                                        s = line % ("ws://" +
                                                    self._nio.ifconfig()[0] +
                                                    ":80")
                                        new_socket.sendall(s)
                                    else:
                                        new_socket.sendall(line)

                        except OSError:
                            # Error while serving webpage
                            pass
                        cout << "close socket (HTTP)" << endl
                        new_socket.close()

        # 各ソケットのprocessを一度実行する
        for client in self._clients:
            client.process()

    def remove_connection(self, connectionIN):
        # self._clients=[,,,,]のconnectionINと一致する要素を探し出し削除
        for con in list(filter(lambda c: c.connection == connectionIN, self._clients)):
            self._clients.remove(con)
        return
