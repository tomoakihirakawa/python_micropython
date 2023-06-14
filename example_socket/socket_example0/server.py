#!/usr/bin/env python3

# server side

import selectors
from socket import *
from base64 import b64encode
from hashlib import sha1
from struct import pack

from time import sleep

print('このコードは，サーバーを理解するためのデモ．')
print('socket(AF_INET, SOCK_STREAM)のSOCK_STREAMは，TCP通信を意味する．')

magicsockey = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

# socket.AF_INETは，ipv4のアドレス族
# socket.SOCK_STREAMは，TCPに起源を持つプロトコル
# socket.socket

lsock = socket(AF_INET, SOCK_STREAM)
# もし，エラーがあれば，socket.errorがかえってくる

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

lsock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
# "0.0.0.0"は，INADDR_ANYとして知られるアドレスでつながるものにつなげる
# "127.0.0.1"は，INADDR_LOOPBACKとして知られ，ローカルホストにつなげるもの
# soc.bind(("0.0.0.0", 9999))
# soc.bind(("192.168.1.17", 8765))

HOST = "127.0.0.1"
# HOST = "10.0.1.9"
PORT = 9999
lsock.bind((HOST, PORT))
lsock.listen(10)
print(lsock.getsockname()[0])
# ソケットがアドレスにバインドされ，リッスン中の場合acceptが使える．
#!すでに同じアドレスからのコネクションを確率してしまっている可能性がある．websocketではそれを管理しなければならない．
print("succeeded! waiting for connection")
conn, raddr = lsock.accept()
#!connはソケット
print('connection socket object: ', conn)
print('remote address: ', raddr)

lsock.setblocking(False)
sel = selectors.DefaultSelector()
sel.register(lsock, selectors.EVENT_READ, data=None)
# -------------------------------------------------------- #
def accept_wrapper(sock):
    conn, raddr = sock.accept()
    print('accepted connection from', raddr)
    conn.setblocking(False)    
    #!dataクラスの定義
    class tmp:
        addr=raddr
        inb=b''
        outb=b''
    data = tmp
    # data = types.SimpleNamespace(addr=raddr, inb=b'', outb=b'')#メンバ変数を簡単に指定してクラスを生成する方法
    events = selectors.EVENT_READ | selectors.EVENT_WRITE#両方の待機
    sel.register(conn, events, data)
    # connは監視するオブジェクト
    # events: このファイルオブジェクトで待機しなければならないイベントです。
    # data: このファイルオブジェクトに関連付けられたオプションの不透明型 (Opaque) データです。例えば、これはクライアントごとのセッション ID を格納するために使用できます。

def service_connection(key,mask):
    rsock = key.fileobj
    data = key.data
    #!dataクラスの定義を忘れたらaccept_wrapperのdataを確認
    if mask & selectors.EVENT_READ:
        recv_data = rsock.recv(1024)
        if recv_data:
            data.outb += recv_data
        else:
            sel.unregister(rsock)
            rsock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            sent = rsock.send(data.outb)
            #sendは送ったデータのバイト数を返す
            data.outb = data.outb[sent:]
            #送ったバイナリデータが削除された

while True:
    #登録されたソケットのうち，通信可能になったものを出力する
    events = sel.select(timeout=None)
    for key, mask in events:
        if key.data is None:
            #selectorに登録されていないコネクションには，dataはない            
            accept_wrapper(key.fileobj)
            #accept_wrapper内部ではdataクラスを付与している．次からこのsocketはdataを持つ
        else:
            service_connection(key, mask)