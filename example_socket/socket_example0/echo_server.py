# server side

from socket import *
from base64 import b64encode
from hashlib import sha1
from struct import pack

from time import sleep

print('このコードは，サーバーを理解するためのデモです．')

magicsockey = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

# socket.AF_INETは，ipv4のアドレス族
# socket.SOCK_STREAMは，TCPに起源を持つプロトコル
# socket.socket

soc = socket(AF_INET, SOCK_STREAM)
# もし，エラーがあれば，socket.errorがかえってくる

#! -------------------------------------------------------- #
# サーバー側のsocketの流れを思い出す:
# socket()
# bind()
# listen()
# accept()
# [connected() from client]
# [written() from client]
# read()
# write()
# [read() bu client]
#! -------------------------------------------------------- #

soc.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
# "0.0.0.0"は，INADDR_ANYとして知られるアドレスでつながるものにつなげる
# "127.0.0.1"は，INADDR_LOOPBACKとして知られ，ローカルホストにつなげるもの
soc.bind(("127.0.0.1", 9999))
# soc.bind(("192.168.1.17", 8765))
# soc.bind(("10.0.1.9", 8765))
soc.listen(10)
print(soc.getsockname()[0])
#ソケットがアドレスにバインドされ，リッスン中の場合acceptが使える．
#!すでに同じアドレスからのコネクションを確率してしまっている可能性がある．websocketではそれを管理しなければならない．
print("succeeded! waiting for connection")
conn, raddr = soc.accept()
#!connはソケット
print('connection socket object: ', conn)
print('remote address: ', raddr)
with conn:
    while True:
        data = conn.recv(1024)
        if not data:
            break
        conn.sendall(data)
