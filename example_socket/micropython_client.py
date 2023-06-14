#!/usr/bin/env python

# WS client example

import ujson
import uasyncio
import uwebsocket as websocket
try:
    import usocket as socket
except:
    import socket


import myNetwork
from myNetwork import WebSocketServer
from myNetwork import WebSocketClient
from myNetwork import WebSocketConnection
from myNetwork import ClientClosedError
from myNetwork import makeAccessPoint
from myNetwork import connectEspToRouter


# ssid = 'TH15'
# password = '8ry37sc2'
ssid = 'TimeCapsule'
password = 'Tomoaki813;'
accesspoint = connectEspToRouter(ssid, password)

# micropythonにはwriteとreadしかない


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = "10.0.1.9"
# HOST = '192.168.1.17'

PORT = 8765
s.connect((HOST, PORT))
s.sendall(b'Hello world')
data = s.recv(1024)
print('received',repr(data))

# async def hello():
#     uri = "ws://192:8765"
#     websocket.write(ujson.dumps({"functions": "test"}))
#     # async with websocket.connect(uri) as websocket:
#     #     name = input("What's your name? ")

#     #     await websocket.send(name)
#     #     print(f"> {name}")

#     #     greeting = await websocket.recv()
#     #     print(f"< {greeting}")

# asyncio.get_event_loop().run_until_complete(hello())
